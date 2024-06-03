import time

start_time = time.time()
# Một số hoạt động cần đo thời gian
time.sleep(2)  # Tạm dừng chương trình trong 2 giây
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Thời gian đã trôi qua: {elapsed_time} giây")
