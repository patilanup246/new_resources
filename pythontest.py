# coding=gbk
import re

string = "С����С��˵��HTC LG SAMSUNG С�� ASUS��ROOT��S OFF��POKEMON GO���֙Cϵ�y�S�ޡ�ˢ�C���ƽ⡢��ُ���ęC��F------------------------------------------��Ħ���Iˢ�C�u��https://tw.bid.yahoo.com/tw/booth/Y1001734322¶�쌣�Iˢ�C�u��...�鿴����С�����͵�����Ϸ��Ա �� 998����ԱWei Cheng��Paul Huang�ǹ���Ա����̬0��������������ȥ 30 ������ 4 ƪ998��Ա������ȥ 30 �����г��� 0 λԼ 3 ��ǰ�� Paul Huang ����"
PATTERN = 'С��˵��(.+?)�鿴����'
pattern = re.compile(PATTERN)
m = pattern.search(string)
print(m.group(1))
print(re.search(r"С��˵��(.+?)�鿴����",string).group(1))
