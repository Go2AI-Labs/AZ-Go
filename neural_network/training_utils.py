"""
Training utilities for neural network wrapper
Extracted from pytorch_classification to reduce dependencies
"""

class AverageMeter(object):
    """Computes and stores the average and current value
       Imported from https://github.com/pytorch/examples/blob/master/imagenet/main.py#L247-L262
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


class Bar(object):
    """Simple progress bar implementation"""
    def __init__(self, message, max_value=None):
        self.message = message
        self.max_value = max_value
        self.index = 0
        self.width = 32
        self.suffix = '%(index)d/%(max)d'
        self.bar_prefix = ' |'
        self.bar_suffix = '| '
        self.empty_fill = ' '
        self.fill = '#'
    
    def start(self):
        self.index = 0
        return self
    
    def next(self):
        self.index += 1
        self.update()
    
    def update(self):
        if self.max_value == 0:
            progress = 1.0
        else:
            progress = self.index / float(self.max_value)
        
        filled_length = int(self.width * progress)
        empty_length = self.width - filled_length
        
        bar = self.fill * filled_length
        empty = self.empty_fill * empty_length
        
        suffix_dict = {'index': self.index, 'max': self.max_value}
        suffix = self.suffix % suffix_dict
        
        line = ''.join([self.message, self.bar_prefix, bar, empty, self.bar_suffix, suffix])
        print('\r' + line, end='', flush=True)
    
    def finish(self):
        print()  # New line after progress bar