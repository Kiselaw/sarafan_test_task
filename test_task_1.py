def numrepeating(n):
    counter = 0
    res = []
    num = 1
    while True:
        if len(res) < (1 + num) * num // 2:
            res.append(num)
            counter += 1
        else:
            num += 1
        if counter == n:
            break
    for i in res:
        print(i, end='')


# Временная сложность - O(n)
# Пространственная сложность - O(n)

# Если нужно, чтобы функция именно возвращала результат,
# то можно через цикл for или map привести все int к str
# и объединить с помощью join.
# На временной сложности это не скажется.

if __name__ == '__main__':
    numrepeating(10)
