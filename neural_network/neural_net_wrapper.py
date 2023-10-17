import os
import sys
import time
from collections import OrderedDict

import numpy as np
import pandas as pd
import torch
import torch.optim as optim
from torch.autograd import Variable

from neural_network.neural_net import NeuralNet
from pytorch_classification.utils import Bar, AverageMeter
from .go_alphanet import AlphaNetMaker as NetMaker
from .go_neural_net import GoNNet

sys.path.append('../')


class NNetWrapper(NeuralNet):
    def __init__(self, game, config):
        super().__init__(game)

        self.config = config

        self.netType = self.config["network_type"]
        if self.netType == 'RES':
            netMkr = NetMaker(game)
            self.nnet = netMkr.makeNet()
        else:
            self.nnet = GoNNet(game, self.config)

        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()

        if torch.cuda.is_available():
            self.nnet.cuda()

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """

        if self.config["optimizer_type"] == "Adam":
            optimizer = optim.Adam(self.nnet.parameters(), lr=self.config["learning_rate"], weight_decay=5e-4)
        elif self.config["optimizer_type"] == "SGD":
            optimizer = optim.SGD(self.nnet.parameters(), lr=self.config["learning_rate"], momentum=0.9)
        else:
            raise KeyError(
                f"Optimizer type '{self.config['optimizer_type']}' is not supported. Please check config.yaml for supported optimizer types.")

        trainLog = {
            'EPOCH': [],
            'P_LOSS': [],
            'V_LOSS': []
        }

        for epoch in range(self.config["epochs"]):
            # print('EPOCH ::: ' + str(epoch + 1))
            trainLog['EPOCH'].append(epoch)
            self.nnet.train()
            data_time = AverageMeter()
            batch_time = AverageMeter()
            pi_losses = AverageMeter()
            v_losses = AverageMeter()
            end = time.time()

            bar = Bar('Training Network', max=int(len(examples) / self.config["batch_size"]))
            batch_idx = 0

            while batch_idx < int(len(examples) / self.config["batch_size"]):
                sample_ids = np.random.randint(len(examples), size=self.config["batch_size"])
                boards, pis, vs = list(zip(*[examples[i] for i in sample_ids]))
                # Convert board histories to stacks as defined in paper
                temp_boards = list(boards)
                for i in range(len(temp_boards)):
                    temp_boards[i] = np.stack(temp_boards[i])
                boards = tuple(temp_boards)

                boards = torch.FloatTensor(np.array(boards).astype(np.float64))
                target_pis = torch.FloatTensor(np.array(pis))
                target_vs = torch.FloatTensor(np.array(vs).astype(np.float64))

                # predict
                if torch.cuda.is_available():
                    boards, target_pis, target_vs = boards.contiguous().cuda(), target_pis.contiguous().cuda(), target_vs.contiguous().cuda()
                boards, target_pis, target_vs = Variable(boards), Variable(target_pis), Variable(target_vs)

                # measure data loading time
                data_time.update(time.time() - end)
                # compute output
                out_pi, out_v = self.nnet(boards)

                l_pi = self.loss_pi(target_pis, out_pi)
                l_v = self.loss_v(target_vs, out_v)
                total_loss = l_pi + l_v

                # record loss
                pi_losses.update(l_pi.data.item(), boards.size(0))
                v_losses.update(l_v.data.item(), boards.size(0))

                # compute gradient and do SGD step
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()

                # measure elapsed time
                batch_time.update(time.time() - end)
                end = time.time()

                batch_idx += 1

                # plot progress
                bar.suffix = '({batch}/{size}) Epoch: {epoch:} | Data: {data:.3f}s | Batch: {bt:.3f}s | Total: {total:} | ETA: {eta:} | Loss_pi: {lpi:.4f} | Loss_v: {lv:.3f} | Batch_size: {batch_size:}'.format(
                    epoch=epoch + 1,
                    batch=batch_idx,
                    size=int(len(examples) / self.config["batch_size"]),
                    data=data_time.avg,
                    bt=batch_time.avg,
                    total=bar.elapsed_td,
                    eta=bar.eta_td,
                    lpi=pi_losses.avg,
                    lv=v_losses.avg,
                    batch_size=self.config["batch_size"]
                )

                bar.next()

            # plot avg pi loss and v loss for all epochs in iteration
            trainLog['P_LOSS'].append(pi_losses.avg)
            trainLog['V_LOSS'].append(v_losses.avg)
            bar.finish()

        return pd.DataFrame(data=trainLog)

    def predict(self, board_list):
        """
        board: np array with board
        """
        # preparing input
        board = np.stack(board_list)
        # print("stack length: ", len(board))
        board = torch.FloatTensor(board.astype(np.float64))
        # print("stack length2: ", len(board))
        if torch.cuda.is_available(): board = board.contiguous().cuda()
        board = Variable(board, requires_grad=False)
        # print("stack length3: ", len(board))
        board = board.view(18, self.board_x, self.board_y)
        # print("stack length4: ", len(board))

        self.nnet.eval()

        pi, v = self.nnet(board)
        return torch.exp(pi).data.cpu().numpy()[0], v.data.cpu().numpy()[0]

    def loss_pi(self, targets, outputs):
        return -torch.sum(targets * outputs) / targets.size()[0]

    def loss_v(self, targets, outputs):
        return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size()[0]

    def save_checkpoint(self, folder='R_checkpoint', filename='R_checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        torch.save({
            'state_dict': self.nnet.state_dict(),
        }, filepath)

    # use cpu_only for maximum compatibility with slowest performance
    def load_checkpoint(self, folder='R_checkpoint', filename='R_checkpoint.pth.tar', cpu_only=False):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise BaseException("No model in path {}".format(filepath))

        if cpu_only:
            checkpoint = torch.load(filepath, map_location=torch.device('cpu'))
        else:
            checkpoint = torch.load(filepath)

        self.nnet.load_state_dict(checkpoint['state_dict'])

    # use cpu_only for maximum compatibility with slowest performance
    def load_checkpoint_from_plain_to_parallel(self, folder='R_checkpoint', filename='R_checkpoint.pth.tar',
                                               cpu_only=False):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise BaseException("No model in path {}".format(filepath))

        if cpu_only:
            checkpoint = torch.load(filepath, map_location=torch.device('cpu'))
        else:
            checkpoint = torch.load(filepath)

        state_dict = checkpoint['state_dict']

        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = "module." + k  # add 'module.' of dataparallel, so it works with examples from plain model
            new_state_dict[name] = v
        self.nnet.load_state_dict(new_state_dict)
