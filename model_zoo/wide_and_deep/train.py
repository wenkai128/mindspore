# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" test_training """
import os
from mindspore import Model, context
from mindspore.train.callback import ModelCheckpoint, CheckpointConfig

from wide_deep.models.WideDeep import PredictWithSigmoid, TrainStepWarp, NetWithLossClass, WideDeepModel
from wide_deep.utils.callbacks import LossCallBack
from wide_deep.data.datasets import create_dataset
from tools.config import Config_WideDeep

context.set_context(model=context.GRAPH_MODE, device_target="Ascend", save_graphs=True)


def get_WideDeep_net(configure):
    WideDeep_net = WideDeepModel(configure)

    loss_net = NetWithLossClass(WideDeep_net, configure)
    train_net = TrainStepWarp(loss_net)
    eval_net = PredictWithSigmoid(WideDeep_net)

    return train_net, eval_net


class ModelBuilder():
    """
    Build the model.
    """
    def __init__(self):
        pass

    def get_hook(self):
        pass

    def get_train_hook(self):
        hooks = []
        callback = LossCallBack()
        hooks.append(callback)
        if int(os.getenv('DEVICE_ID')) == 0:
            pass
        return hooks

    def get_net(self, configure):
        return get_WideDeep_net(configure)


def test_train(configure):
    """
    test_train
    """
    data_path = configure.data_path
    batch_size = configure.batch_size
    epochs = configure.epochs
    ds_train = create_dataset(data_path, train_mode=True, epochs=epochs, batch_size=batch_size)
    print("ds_train.size: {}".format(ds_train.get_dataset_size()))

    net_builder = ModelBuilder()
    train_net, _ = net_builder.get_net(configure)
    train_net.set_train()

    model = Model(train_net)
    callback = LossCallBack(configure)
    ckptconfig = CheckpointConfig(save_checkpoint_steps=1,
                                  keep_checkpoint_max=5)
    ckpoint_cb = ModelCheckpoint(prefix='widedeep_train', directory=configure.ckpt_path, config=ckptconfig)
    model.train(epochs, ds_train, callbacks=[callback, ckpoint_cb])


if __name__ == "__main__":
    config = Config_WideDeep()
    config.argparse_init()

    test_train(config)
