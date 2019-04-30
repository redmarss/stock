import myGlobal.myCls.multiProcess as mp

import myGlobal.globalFunction as gf



def test(code):
    print(code)



if __name__ == '__main__':
    [test(code) for code in [1,2,3,4,5,6,7,8]]