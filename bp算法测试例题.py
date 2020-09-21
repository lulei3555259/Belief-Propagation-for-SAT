# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 22:05:34 2020

@author: lulei
"""

import numpy as np
from random import shuffle
import networkx as nx
from fractions import Fraction

def factor_graph(cnf, N, M):
    G = nx.Graph()
    G.add_nodes_from(np.arange(N + M) + 1)

    for i in range(M):
        B = np.abs(cnf[i]) #遍历cnf公式每一行
        J = -np.sign(cnf[i]) #赋值J，正文字为-1
        G.add_edges_from([(N + i + 1, x) for x in B]) #子句a向变元添加边
        for j in range(len(B)): #B[i]是变元
            G[N + i + 1][ B[j] ]['J'] = J[j]
            #G[N + i + 1][ B[j] ]['u'] = randint(0,1) #0,1随机赋值
            #G[N + i + 1][ B[j] ]['h'] = 0
            G[N + i + 1][ B[j] ]['delta'] = np.random.rand(1) #0到1随机数赋值
    return G


def belief_prop(G, tmax, eps):
    for t in range(tmax):
        d = np.array(list(nx.get_edge_attributes(G, 'delta').values()))
        G = bp_update(G)
        d_ = np.array(list(nx.get_edge_attributes(G, 'delta').values()))
        if np.all(np.abs(d - d_) < eps):
            BPstatus = '收敛'
            print(t)
            print(nx.get_edge_attributes(G, 'delta').items())
            return BPstatus
    BPstatus = '不收敛'
    return BPstatus
    
    
def bp_update(G):
    L = list(G.edges())
    shuffle(L)

    for (i,a) in L:
        # 计算空腔
        for j in G.neighbors(a):
            if i == j: #V(a)\i
                continue
            prod_tmp = np.ones(2) #[1,1]
            for b in G.neighbors(j):
                if b == a: #V(j)\a
                    continue
                theta = int(np.heaviside(G[a][j]['J'] * G[b][j]['J'], 0)) #如果乘积大于0，代表相同
                prod_tmp[theta] *= (1 - G[b][j]['delta']) #p=1是V_s，p=0是V_u
            G[a][j]['P_u'] = prod_tmp[1]
            G[a][j]['P_s'] = prod_tmp[0]
                    
        # 计算调查信息
        G[a][i]['delta'] = 1
        for j in G.neighbors(a):
            if i == j: #V(a)\i
                continue
            tot = G[a][j]['P_u'] + G[a][j]['P_s']
            p = G[a][j]['P_u'] / tot
            G[a][i]['delta'] *= p
    return G

def belief_id(G, N, M):
    u = []
    for i in range(N):
        p_plus = 1
        p_minus = 1
        for a in G.neighbors(i+1):
            if G[a][ i+1 ]['J'] == 1:
                p_minus *= 1 - G[a][ i+1 ]['delta']
            else:
                p_plus *= 1 - G[a][ i+1 ]['delta']
        p = p_minus / (p_minus + p_plus)
        u.append(p)
    return u
            

if __name__ == '__main__':
    cnf = [
           [1],
           [-2],
           [-1,2,3],
           [-3,4],
           [3,5],
           [4],
           [4,-7],
           [5,8],
           [-5,6]
           ]
    np.array(cnf) 
    N = 8
    M = 9
    G = factor_graph(cnf, N, M)
    hha = belief_prop(G,20,1e-3)
    print(hha)
    u = belief_id(G, N, M)
    print(u)
