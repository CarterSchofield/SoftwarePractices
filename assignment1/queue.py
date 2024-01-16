class SimpleQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if len(self.queue) == 0:
            return None
        return self.queue.pop(0)

    def display(self):
        return self.queue

# Creating an instance of SimpleQueue
my_queue = SimpleQueue()

# Adding some strings to the queue
my_queue.enqueue("Hello")
my_queue.enqueue("World")
my_queue.enqueue("Python")

# Printing out the queue
print("Queue contents:", my_queue.display())

# Dequeue and print each item
print("Dequeueing...")
while True:
    item = my_queue.dequeue()
    if item is None:
        break
    print("Dequeued:", item)
