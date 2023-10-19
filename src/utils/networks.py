from pathlib import Path
from sys import argv
import numpy as np
import re


class NN(list):
  RELU, AFFINE = 0, 1

  def __init__(self, weights:list, biases:list, activations:list):
    super().__init__()
    self.nlayers = len(weights)

    assert(self.nlayers == len(biases))
    assert(all([x == NN.RELU or x == NN.AFFINE for x in activations]))

    for i, (w, b) in enumerate(zip(weights, biases)):
      assert(isinstance(w, np.ndarray) and isinstance(b, np.ndarray))
      assert(w.ndim == 2 and b.ndim == 1)
      assert(w.shape[0] == b.shape[0])
      assert(i < 1 or w.shape[1] == weights[i-1].shape[0])
    self.ninputs = weights[0].shape[1]
    self.noutputs = weights[-1].shape[0]

    self.lb, self.ub = 0, 1

    self.weights = weights
    self.biases = biases
    self.activations = activations
    for w, b, a in zip(reversed(weights), reversed(biases), reversed(activations)):
      super().append((b.shape[0], w, b, a))

  def run_vector(self, inputs:np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    acc = inputs
    activations = []
    for _, w, b, a in reversed(self):
      acc = np.dot(w, acc) + b
      activations.append(acc >= 0)
      if a == NN.RELU:
        acc[acc < 0] = 0
    return acc, activations
  
  def classify(self, inputs:np.ndarray) -> int:
    return np.argmax(self.run_vector(inputs)[0])

  def run_z(self, inputs:np.ndarray, i:int) -> tuple[float, list[np.ndarray]]:
    acc, activations = self.run_vector(inputs)
    z:float = acc.pop(i) # type: ignore
    return [z-y for y in acc], activations # type: ignore

  def run_ij(self, inputs:np.ndarray, i:int, j:int) -> tuple[float, list[np.ndarray]]:
    acc, activations = self.run_vector(inputs)
    return acc[i] - acc[j], activations

  @staticmethod
  def read_python(path: Path) -> 'NN':
    with open(path, 'r') as f:
      file = f.read().replace(" ", "").replace("\t", "")
    lines = file.split('\n')
    weights_list, biases_list = [], []
    for line in lines:
      before_comment = line.split('#')[0]
      if before_comment.startswith("assume") or before_comment.startswith("assert"):
        continue
      if len(before_comment) == 0:
        continue
      if before_comment.startswith("ReLU"):
        continue
      id, eqs = before_comment.split("=")
      i = int(id[1]) - 1
      if len(weights_list) == i:
        weights_list.append([])
        biases_list.append([])
      coeffs = np.array([float(x) for x in re.findall('\((.*?)\)', eqs)])
      weights_list[-1].append(coeffs[:-1])
      biases_list[-1].append(coeffs[-1])

    weights, biases = [], []
    for w in weights_list:
      weights.append(np.array(w))
    for b in biases_list:
      biases.append(np.array(b))
    activations = [NN.RELU for _ in biases] + [NN.AFFINE]
    return NN(weights, biases, activations)

  def output_space_composition(self, l:int, u:int, ntests:int=100000) -> dict[int,int]:
    tests = [np.random.rand(self.ninputs) * (u - l) + l for _ in range(ntests)]
    outputs = [self.run_vector(test)[0] for test in tests]
    max_indices = [np.argmax(x) for x in outputs]
    unique, counts = np.unique(max_indices, return_counts=True)
    return dict(zip(unique, counts))

  def input_from_output(self, output_index:int, l:int, u:int, ntests:int=100000) -> tuple[np.ndarray, list[np.ndarray]]:
    for _ in range(ntests):
      input_test = np.random.rand(self.ninputs) * (u - l) + l
      output_test, activations = self.run_vector(input_test)
      if output_index == np.argmax(output_test):
        return input_test, activations
    raise Exception('failed to find an input')

  def set_input_bounds(self, lb:int, ub:int) -> None:
    self.lb, self.ub = lb, ub
