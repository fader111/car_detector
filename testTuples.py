
resolution = [23,45]
width, height = resolution
resolution.append(34)

    #fwidth, fheight = raw_resolution(resolution)
print (width, height)
print (resolution)
ramki = [1,2,3,4,5]
gen = [0 for i in range(len(ramki))]
print('gen-',gen)

a=[1,0,0]
b=[0,1,1]
print ('OR',a or b)
if a or b:
	print ('a,b',a,b)

x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
y = [2, 2, 2, 3, 6, 9, 8, 8, 8, 9, 10]
for i in set(x) & set(y):
    print('число {} встречается {} раз(а)'.format(i,max(x.count(i),y.count(i))))	

list1 = [1, 2, 3, 4, 5, 6, 7]
list2 = [3, 4, 3, 4, 2, 6, 9]

#new_list = list(map(|, list1, list2))
new_list = [i or j for i,j in zip(list1, list2)]
print ('list1',list1)
print ('list2',list2)
print ('new_list',new_list)
