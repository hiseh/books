<!--
 * @Author: Hiseh
 * @Date: 2020-08-15 21:43:19
 * @LastEditors: Hiseh
 * @LastEditTime: 2020-08-15 22:23:22
 * @Description: 
-->

# Python对象生命周期

上一页我们知道对象的**元数据**保存在`PyTypeObject`实例里，其中就包括如何创建和销毁对象的信息，可大胆推测，**实例对象**就是由**类型对象**创建的。这里我们还是以`float`类型为例，看看Python如何创建对象的。

## 创建对象

在*Include/floatobject.h*里能看到有两个创建`float`对象的函数，一个是直接用`double`参数创建，一个是从基础类创建，显然第一个应该更简单：

```c
PyAPI_FUNC(PyObject *) PyFloat_FromDouble(double);
PyAPI_FUNC(PyObject *) PyFloat_FromString(PyObject*);
```

`PyFloat_FromDouble`代码如下：

```c
PyObject *PyFloat_FromDouble(double fval) {
    PyFloatObject *op = free_list;
    if (op != NULL) {
        free_list = (PyFloatObject *)Py_TYPE(op);
        numfree--;
    } else {
        op = (PyFloatObject *)PyObject_MALLOC(sizeof(PyFloatObject));
        if (!op) return PyErr_NoMemory();
    }
    /* Inline PyObject_New */
    (void)PyObject_INIT(op, &PyFloat_Type);
    op->ob_fval = fval;
    return (PyObject *)op;
}
```

的确很简单，关键信息就两行，先为`PyFloatObject`分配内存，然后给`ob_fval`赋值。

再看看第二种创建方式，代码比较长，我们只看重点：

```c
#define _Py_NewReference(op) (                          \
    _Py_INC_TPALLOCS(op) _Py_COUNT_ALLOCS_COMMA         \
    _Py_INC_REFTOTAL  _Py_REF_DEBUG_COMMA               \
    Py_REFCNT(op) = 1)
    
PyObject *PyObject_Init(PyObject *op, PyTypeObject *tp) {
    Py_TYPE(op) = tp;
    _Py_NewReference(op);
    return op;
}
```

逻辑也不是很复杂：

1. 首先执行`tp_new`函数，如果没找到，则去`tp_base`指定的父类查找。因为`PyObject`是最终的根，所以总能找到一个可执行的`tp_new`。
1. 在**类型对象中**查找`tp_basicsize`，进而完成申请内存操作。因为`PyType_Type`是虽有类型对象的根，所有总能找到一个可用的`tp_basicsize`来申请内存。
1. 执行`tp_init`，完成初始化对象工作。

## 调用对象

当对象被调用时，Python会执行`tp_call`函数函数指针，它会调用`buildin.__import__`，加载真正需要执行的函数。
