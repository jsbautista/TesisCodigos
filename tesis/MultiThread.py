from queue import Queue
from threading import Thread

def foo(bar):
    print ('hello {0}'.format(bar))
    return 'foo'+'hello {0}'.format(bar)

que = Queue()           # Python 3.x

threads_list = list()

t = Thread(target=lambda q, arg1: q.put(foo(arg1)), args=(que, 'perros!'))
t.start()
threads_list.append(t)

# Add more threads here
t2 = Thread(target=lambda q, arg1: q.put(foo(arg1)), args=(que, 'k!'))
t2.start()
threads_list.append(t2)
t3 = Thread(target=lambda q, arg1: q.put(foo(arg1)), args=(que, 'j!'))
t3.start()
threads_list.append(t3)

# Join all the threads
for k in threads_list:
    k.join()

a = "";
# Check thread's return value
while not que.empty():
    result = que.get()
    a+=result

print (a)