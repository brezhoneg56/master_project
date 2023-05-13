#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 13 11:23:47 2023

@author: julien
"""

def function1():
    print("koukou")
    ans=input("Enter name: ")
    return(ans)

def function2(ans):
    print(ans)
    

function2(function1())