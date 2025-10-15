import collections
def gen_bin_tree(height = 3, root = 11, l_b=lambda x: x ** 2, r_b=lambda y : 2 + y ** 2):
    '''
    Функция, создающая бинарное дерево
    height: высота дерева
    root: значение корневого узла
    l_b: функция для вычисления левого потомка
    r_b: функция для вычисления правого потомка
    '''

    if height == 0:
        return None
    if height == 1:
        return {str(root): []}
    ''' Возвращает None если высота дерева 0 и корень если высота дерева 1'''


    root_base = {'value': root, 'left': None, 'right': None}

    # очередь для обхода уровня
    queue = collections.deque()
    queue.append((root_base, 1))  # (узел, текущий уровень)

    while queue:
        current_root, level = queue.popleft() #распаковка кортежа
        if level < height:
            # левая ветка
            left_base = l_b(current_root["value"]) #взяли корень и умножили на 3
            left_root = {"value": left_base} #1 значение в левую ветку и база для следующих веток
            current_root["left"] = left_root # занесли левую ветку в текущее дерево
            queue.append([left_root, level + 1]) #переходим к следующему уровню
            # правая ветка
            right_base = r_b(current_root["value"])
            right_root = {"value": right_base}
            current_root["right"] = right_root
            queue.append([right_root, level + 1])

    return root_base
    ''' Возвращает дерево в виде словаря'''

def display_tree_json(tree):
    """
    JSON-представление дерева.
    """
    import json
    print("\nJSON ПРЕДСТАВЛЕНИЕ:")
    print("=" * 30)
    print(json.dumps(tree, indent=3))

def main():
    height = int(input('высота дерева: '))
    root = int(input('корень дерева: '))
    tree = gen_bin_tree(height, root)
    print('ваше дерево: : ', tree)

if __name__ == '__main__':
    main()

# print(gen_bin_tree())