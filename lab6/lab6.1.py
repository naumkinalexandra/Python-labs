def left_branch(root: int) -> int:
    '''Левый потомок'''
    return root ** 2

def right_branch(root: int) -> int:
    ''' Правый потомок '''
    return 2+root**2

def build_tree_recursive(height = 3, root = 11, l_b=left_branch, r_b=right_branch):
    '''
    Функция, создающая бинарное дерево
    height: высота дерева
    root: значение корневого узла
    l_b: функция для вычисления левого потомка (по умолчанию left_branch)
    r_b: функция для вычисления правого потомка (по умолчанию right_branch)
    '''

    if type(height) != int:
        return "Введите целое число для высоты"
    if type(root) != int and type(root) != float :
        return "Введите числовое значение для корня"
    '''' Возвращает запрос ввести правильный тип данных для высоты или корня'''

    if height == 0:
        return None
    if height == 1:
        return {str(root): []}

    ''' Возвращает None если высота дерева 0 и корень если высота дерева 1'''

    left_tree = build_tree_recursive(height - 1, l_b(root), l_b, r_b) if height > 1 else []
    right_tree = build_tree_recursive(height - 1, r_b(root), l_b, r_b) if height > 1 else []

    return {str(root): [left_tree, right_tree]}
    ''' Возвращает дерево в виде словаря'''

def main():
    height = int(input('высота дерева: '))
    root = int(input('корень дерева: '))
    tree = build_tree_recursive(height, root)
    print('ваше дерево: : ', tree)

if __name__ == '__main__':
    main()