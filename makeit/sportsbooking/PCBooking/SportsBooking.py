from GetInfo import GetInfo
from multiprocessing import Process
import time

if __name__ == "__main__":
    print("开始等待")
    # while True:
    #     if time.localtime().tm_hour == 7 and time.localtime().tm_min == 0 and time.localtime().tm_sec == 0:
    #         time.sleep(0.5)
    #         break
    #a = GetInfo("21904031", "lyclsxlmw5471")
    b = GetInfo("31805072","ZZss197356428")
    # c = GetInfo("31904173", "rui1996??")
    # d = GetInfo("21804131", "xh2641127668")
    # e = GetInfo("31804162", "zlzl5216")
    # while True:
    #     if time.localtime().tm_hour == 7 and time.localtime().tm_min == 0 and time.localtime().tm_sec == 0:
    #         time.sleep(0.05)
    #         break
    # a.get_login()
    b.get_login()
    # c.get_login()
    # d.get_login()
    # e.get_login()
    # p1 = Process(target=a.generate_order, args=("badminton", [[3, "11:00-12:00"], [4, "12:00-13:00"], ], 11))
    p2 = Process(target=b.generate_order, args=("badminton", [[5, "19:00-20:00"], ], 11 ))
    # p2 = Process(target=b.keep_order)
    # p3 = Process(target=d.generate_order, args=("badminton", [[4, "19:00-20:00"], [5, "20:00-21:00"], ], 11))
    # p4 = Process(target=b.generate_order, args=("badminton", [[1, "15:00-16:00"], [2, "16:00-17:00"], ], 12))
    # p5 = Process(target=a.generate_order, args=("badminton", [[3, "17:00-18:00"], [4, "18:00-19:00"], ], 12))
    # p6 = Process(target=c.generate_order, args=("badminton", [[4, "19:00-20:00"], [5, "20:00-21:00"], ], 12))
    # p7 = Process(target=c.generate_order, args=("badminton", [[1, "15:00-16:00"], [2, "16:00-17:00"], ], 14))
    # p8 = Process(target=d.generate_order, args=("badminton", [[3, "17:00-18:00"], [4, "18:00-19:00"], ], 14))
    # p9 = Process(target=a.generate_order, args=("badminton", [[4, "19:00-20:00"], [5, "20:00-21:00"], ], 14))
    # p10 = Process(target=d.generate_order, args=("badminton", [[1, "15:00-16:00"], [2, "16:00-17:00"], ], 15))
    # p11 = Process(target=c.generate_order, args=("badminton", [[3, "17:00-18:00"], [4, "18:00-19:00"], ], 15))
    # p12 = Process(target=b.generate_order, args=("badminton", [[4, "19:00-20:00"], [5, "20:00-21:00"], ], 15))
    # p13 = Process(target=e.generate_order, args=(
    # "basketball", [[1, "15:00-15:30"], [2, "15:30-16:00"], [3, "16:00-16:30"], [4, "16:30-17:00"]], "1-半1"))
    # p14 = Process(target=e.generate_order, args=(
    # "basketball", [[5, "17:00-17:30"], [6, "17:30-18:00"], [7, "18:00-18:30"], [8, "18:30-19:00"]], "1-半1"))

    # p1.start()
    p2.start()
    # p3.start()
    # p4.start()
    # p5.start()
    # p6.start()
    # p7.start()
    # p8.start()
    # p9.start()
    # p10.start()
    # p11.start()
    # p12.start()
    # p13.start()
    # p14.start()
    # p1.join()
    p2.join()
    # p3.join()
    # p4.join()
    # p5.join()
    # p6.join()
    # p7.join()
    # p8.join()
    # p9.join()
    # p10.join()
    # p11.join()
    # p12.join()
    # p13.join()
    # p14.join()
    for i in range(2):
        time.sleep(60*20)
        print("执行第" + str(i) + "次")
        b.keep_order()