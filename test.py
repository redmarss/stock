import myGlobal.myCls.multiProcess as mp

import myGlobal.globalFunction as gf


@mp.threads(10)
def test(code,test):
    print(str(code)+test)




if __name__ == '__main__':
    [test(code,'123') for code in [1,2,3,4,5,6,7,8]]