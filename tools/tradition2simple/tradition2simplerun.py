from tools.tradition2simple.langconv import *


def simple2tradition(line):
    # 将简体转换成繁体
    line = Converter('zh-hant').convert(line)
    line = line
    return line


def tradition2simple(line):
    # 将繁体转换成简体
    line = Converter('zh-hans').convert(line)
    line = line
    return line

if __name__ == '__main__':
    print(tradition2simple("如有"))