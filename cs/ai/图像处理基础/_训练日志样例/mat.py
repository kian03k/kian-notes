import re
import numpy as np
import matplotlib.pyplot as plt

f = open(r"train_log.txt", encoding='utf-8')
get_list = ['total_loss', 'iou_loss', 'conf_loss', 'cls_loss']  # 'epoch',
used_list = []
txt_list = list(filter(lambda x: 'after_iter' in x and 'iter: 40/72' in x, f.readlines()))
# splits_list = list(map(lambda x: re.split('[,\-]', x), txt_list))
for i in txt_list:
    temp_list = []
    splits_list = re.split('[,\-]', i)
    for j in splits_list:
        n = j.replace(' ', '')
        n_list = n.split(':')
        if n_list[0] in get_list:
            temp_list.append(float(n_list[1]))
    used_list.append(temp_list)
    # temp_list.clear()导致已赋值的的变量也进行更改
print(used_list)
print(type(used_list))
used_np = np.array(used_list)


def get_total_loss():
    print('')
    x = np.arange(0, len(used_list), 1)
    y = used_np[:, 0]
    plt.title('total_loss变化曲线')
    plt.xlabel('epoch')
    plt.ylabel('total_loss')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使中文可以运行
    plt.plot(x, y)
    plt.savefig('total_loss.png')


def get_iou_loss():
    print('')
    x = np.arange(0, len(used_list), 1)
    y = used_np[:, 1]
    plt.title('iou_loss变化曲线')
    plt.xlabel('epoch')
    plt.ylabel('iou_loss')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使中文可以运行
    plt.plot(x, y)
    plt.savefig('iou_loss.png')


def get_conf_loss():
    print('')
    x = np.arange(0, len(used_list), 1)
    y = used_np[:, 2]
    plt.title('conf_loss变化曲线')
    plt.xlabel('epoch')
    plt.ylabel('conf_loss')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使中文可以运行
    plt.plot(x, y)
    plt.savefig('conf_loss.png')


def get_cls_loss():
    print('')
    x = np.arange(0, len(used_list), 1)
    y = used_np[:, 3]
    plt.title('cls_loss变化曲线')
    plt.xlabel('epoch')
    plt.ylabel('cls_loss')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使中文可以运行
    plt.plot(x, y)
    plt.savefig('cls_loss.png')

def get_totel():
    # f, ax = plt.subplots(2, 2)
    # plt.figure(figsize=(12,12))
    f, ax = plt.subplots(2, 2, figsize=(14, 12))
    f.suptitle('训练结果展示',fontsize=22)

    ax[0][0].set_title('total_loss变化曲线')
    ax[0][1].set_title('iou_loss变化曲线')
    ax[1][0].set_title('conf_loss变化曲线')
    ax[1][1].set_title('cls_loss变化曲线')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 使中文可以运行

    plt.subplot(2, 2, 1)
    x = np.arange(0, len(used_list), 1)
    y = used_np[:, 0]
    plt.xlabel('epoch')
    plt.ylabel('total_loss')
    plt.plot(x, y)

    plt.subplot(2, 2, 2)
    x = np.arange(0, len(used_list), 1)
    y = used_np[:, 1]
    plt.xlabel('epoch')
    plt.ylabel('iou_loss')
    plt.plot(x, y)

    plt.subplot(2, 2, 3)
    x = np.arange(0, len(used_list), 1)
    y = used_np[:, 2]
    plt.xlabel('epoch')
    plt.ylabel('conf_loss')
    plt.plot(x, y)

    plt.subplot(2, 2, 4)
    x = np.arange(0, len(used_list), 1)
    y = used_np[:, 3]
    plt.xlabel('epoch')
    plt.ylabel('cls_loss')
    plt.plot(x, y)
    plt.savefig('totel.png')
    # plt.show()


if __name__ == "__main__":
    print('')
    # get_total_loss()
    # get_iou_loss()
    # get_conf_loss()
    # get_cls_loss()
    # get_totel()
