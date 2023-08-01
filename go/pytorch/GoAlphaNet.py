import torch.utils.model_zoo as model_zoo
import torch.nn as nn
import math
import torch.nn.functional as F

from torchvision.models.resnet import ResNet

__all__ = ['ResNet']

model_urls = {
    'resnet18': 'https://download.pytorch.org/models/resnet18-5c106cde.pth',
    'resnet34': 'https://download.pytorch.org/models/resnet34-333f7ec4.pth',
    'resnet50': 'https://download.pytorch.org/models/resnet50-19c8e357.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-b121ed2d.pth',
}


def conv3x3(in_planes, out_planes, stride=1):
    "3x3 convolution with padding"
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)


class AlphaBottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(AlphaBottleneck, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class AlphaBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(AlphaBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class AlphaNet(ResNet):
    def __init__(self, game, layers):
        block = AlphaBlock
        self.board_x, self.board_y = game.getBoardSize()
        self.action_size = game.getActionSize()
        outputShift = 1 if self.board_x in [6, 7, 11] else 4
        self.inplanes = 128  # changed from 64

        super(ResNet, self).__init__()

        self.conv1 = nn.Conv2d(9, 128, kernel_size=5, stride=1, padding=2,
                               bias=False)
        self.bn1 = nn.BatchNorm2d(128)
        self.relu = nn.ReLU(inplace=True)

        self.layer1 = self._make_layer(block, 128, layers[0], stride=1)
        self.layer2 = self._make_layer(block, 128, layers[1])  # stride = 2
        self.layer3 = self._make_layer(block, 128, layers[2])
        self.layer4 = self._make_layer(block, 128, layers[3])
        self.avgpool = nn.AvgPool2d(3, stride=1)  # changed from 2
        # self.avgpool = nn.AdaptiveAvgPool2d() #changed from 2
        self.fc_p = nn.Linear(3200 * block.expansion * outputShift,
                              self.action_size)  # changed from 512*block.expansion*outputShift, self.action_size
        self.fc_v = nn.Linear(3200 * block.expansion * outputShift, 1)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def forward(self, x):
        # print("forward")
        x = x.view(-1, 9, self.board_x, self.board_y)
        # print("Before conv1:", x.size())
        x = self.conv1(x)
        # print("After conv1:", x.size())
        x = self.bn1(x)
        x = self.relu(x)

        x = self.layer1(x)
        # print("After layer1:", x.size())
        x = self.layer2(x)
        # print("After layer2:", x.size())
        x = self.layer3(x)
        # print("After layer3:", x.size())
        x = self.layer4(x)
        # print("After layer4:", x.size())

        try:
            x = self.avgpool(x)
        except:
            pass
        # print("After avgpool:", x.size())

        x = x.view(x.size(0), -1)
        # print("After view:", x.size())
        p = self.fc_p(x)
        v = self.fc_v(x)
        # print("After p:", p.size())
        # print("After v:", v.size())
        return F.log_softmax(p, dim=1), F.tanh(v)


class AlphaNetMaker:
    def __init__(self, game):
        self.n, self.n = game.getBoardSize()
        self.game = game

    def makeNet(self):
        if self.n <= 11:
            print("[LOG]:Input board size is {}x{}, using ResNet-{}.".format(self.n, self.n, 18))
            return self.resnet18(self.game)
        else:
            print("[LOG]:Input board size is {}x{}, using ResNet-{}.".format(self.n, self.n, 34))
            return self.resnet34(self.game)

    def resnet18(self, game, pretrained=False):
        """Constructs a ResNet-18 model.

        Args:
            pretrained (bool): If True, returns a model pre-trained on ImageNet
        """
        model = AlphaNet(game, [2, 2, 2, 2])
        if pretrained:
            model.load_state_dict(model_zoo.load_url(model_urls['resnet18']))
        return model

    def resnet34(self, game, pretrained=False, **kwargs):
        """Constructs a ResNet-34 model.

        Args:
            pretrained (bool): If True, returns a model pre-trained on ImageNet
        """
        model = AlphaNet(game, [3, 4, 6, 3])
        if pretrained:
            model.load_state_dict(model_zoo.load_url(model_urls['resnet34']))
        return model
