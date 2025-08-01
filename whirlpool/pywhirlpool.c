/* 
 * This is just a wrapper to the Whirlpool hashing function. 
 * The Whirlpool reference implementations are public domain, 
 * as is this code. 
 */ 
#include <Python.h> 
#include "Whirlpool.c" 

#if PY_MAJOR_VERSION >= 3 
#ifndef GET_BUFFER_VIEW_OR_ERROUT /* Same as defined in hashlib.h */ 
#define GET_BUFFER_VIEW_OR_ERROUT(obj, viewp) do { \ 
    if (PyUnicode_Check((obj))) { \ 
        PyErr_SetString(PyExc_TypeError, \ 
                        "Unicode-objects must be encoded before hashing");\ 
        return NULL; \ 
    } \ 
    if (!PyObject_CheckBuffer((obj))) { \ 
        PyErr_SetString(PyExc_TypeError, \ 
                        "object supporting the buffer API required"); \ 
        return NULL; \ 
    } \ 
    if (PyObject_GetBuffer((obj), (viewp), PyBUF_SIMPLE) == -1) { \ 
        return NULL; \ 
    } \ 
    if ((viewp)->ndim > 1) { \ 
        PyErr_SetString(PyExc_BufferError, \ 
                        "Buffer must be single dimension"); \ 
        PyBuffer_Release((viewp)); \ 
        return NULL; \ 
    } \ 
} while(0); 
#endif 
#endif 

#if PY_MAJOR_VERSION >= 3 && !defined(PYPY_VERSION) 
#define HEXDIGITS(c) Py_hexdigits[c] 
#else 
#define HEXDIGITS(c) ((c>9) ? c+'a'-10 : c+'0') 
#endif 

// CRITICAL FIX: Add backward compatibility for Py_SET_TYPE 
#if PY_VERSION_HEX < 0x030900A4 && !defined(Py_SET_TYPE) 
#if !defined(__cplusplus) && defined(_MSC_VER) && _MSC_VER < 1900 
#define inline __inline 
#endif 
static inline void _Py_SET_TYPE(PyObject *ob, PyTypeObject *type) { ob->ob_type = type; } 
#define Py_SET_TYPE(ob, type) _Py_SET_TYPE((PyObject*)(ob), type) 
#endif 

typedef struct { 
    PyObject_HEAD 
    NESSIEstruct whirlpool; /* the context holder */ 
} whirlpoolobject; 

static PyTypeObject Whirlpooltype; 

#define is_whirlpoolobject(v) ((v)->ob_type == &Whirlpooltype) 

static whirlpoolobject * 
newwhirlpoolobject(void) 
{ 
    whirlpoolobject *wpp; 
    wpp = PyObject_New(whirlpoolobject, &Whirlpooltype); 
    if (wpp == NULL) 
        return NULL; 
    NESSIEinit(&wpp->whirlpool); /* actual initialisation */ 
    return wpp; 
} 

/* Whirlpool methods */ 

static void whirlpool_dealloc(whirlpoolobject *wpp) 
{ 
    PyObject_Del(wpp); 
} 

/* Whirlpool methods-as-attributes */ 

static PyObject * 
whirlpool_update(whirlpoolobject *self, PyObject *args) 
{ 
    Py_buffer view = { 0 }; 
#if PY_MAJOR_VERSION >= 3 
    PyObject *obj = NULL; 
    if (!PyArg_ParseTuple(args, "O:update", &obj)) 
        return NULL; 
    if (obj) 
        GET_BUFFER_VIEW_OR_ERROUT(obj, &view); 
#else 
    if (!PyArg_ParseTuple(args, "s*:update", &view)) 
        return NULL; 
#endif 
    NESSIEadd((unsigned char*)view.buf, Py_SAFE_DOWNCAST(view.len, Py_ssize_t, unsigned int) * 8, &self->whirlpool); 
    PyBuffer_Release(&view); 
    Py_RETURN_NONE; 
} 

static PyObject * 
whirlpool_digest(whirlpoolobject *self) 
{ 
    NESSIEstruct wpContext; 
    unsigned char digest[DIGESTBYTES]; 
    /* Make a temporary copy, and perform the final */ 
    wpContext = self->whirlpool; 
    NESSIEfinalize(&wpContext, digest); 
#if PY_MAJOR_VERSION >= 3 
    return PyBytes_FromStringAndSize((const char *)digest, sizeof(digest)); 
#else 
    return PyString_FromStringAndSize((const char *)digest, sizeof(digest)); 
#endif 
} 

static PyObject * 
whirlpool_hexdigest(whirlpoolobject *self) 
{ 
    NESSIEstruct wpContext; 
    PyObject *retval; 
    unsigned char digest[DIGESTBYTES]; 
#if PY_MAJOR_VERSION >= 3 
    Py_UCS1 *hexdigest; 
#else 
    char *hexdigest; 
#endif 
    unsigned int i, j; 
    /* Get the raw (binary) digest value */ 
    wpContext = self->whirlpool; 
    NESSIEfinalize(&wpContext, digest); 
    /* Create a new string */ 
#if PY_MAJOR_VERSION >= 3 
    retval = PyUnicode_New(sizeof(digest) * 2, 127); 
#else 
    retval = PyString_FromStringAndSize(NULL, sizeof(digest) * 2); 
#endif 
    if (!retval) 
        return NULL; 
#if PY_MAJOR_VERSION >= 3 
    hexdigest = PyUnicode_1BYTE_DATA(retval); 
#else 
    hexdigest = PyString_AsString(retval); 
#endif 
    if (!hexdigest) { 
        Py_DECREF(retval); 
        return NULL; 
    } 
    /* Make hex version of the digest */ 
    for(i=j=0; i<sizeof(digest); i++) { 
        unsigned char c; 
        c = (digest[i] >> 4) & 0xf; 
        hexdigest[j++] = HEXDIGITS(c); 
        c = (digest[i] & 0xf); 
        hexdigest[j++] = HEXDIGITS(c); 
    } 
    return retval; 
} 

static PyObject * 
whirlpool_copy(whirlpoolobject *self) 
{ 
    whirlpoolobject *wpp; 
    if ((wpp = newwhirlpoolobject()) == NULL) 
        return NULL; 
    wpp->whirlpool = self->whirlpool; 
    return (PyObject *)wpp; 
} 

static PyMethodDef whirlpool_methods[] = { 
    {"update", (PyCFunction)whirlpool_update, METH_VARARGS, "Update hash with data"}, 
    {"digest", (PyCFunction)whirlpool_digest, METH_NOARGS, "Return digest as bytes"}, 
    {"hexdigest", (PyCFunction)whirlpool_hexdigest, METH_NOARGS, "Return digest as hex string"}, 
    {"copy", (PyCFunction)whirlpool_copy, METH_NOARGS, "Return copy of hash object"}, 
    {NULL, NULL} /* sentinel */ 
}; 

static PyObject * 
whirlpool_get_block_size(PyObject *self, void *closure) 
{ 
#if PY_MAJOR_VERSION >= 3 
    return PyLong_FromLong(WBLOCKBYTES); 
#else 
    return PyInt_FromLong(WBLOCKBYTES); 
#endif 
} 

static PyObject * 
whirlpool_get_digest_size(PyObject *self, void *closure) 
{ 
#if PY_MAJOR_VERSION >= 3 
    return PyLong_FromLong(DIGESTBYTES); 
#else 
    return PyInt_FromLong(DIGESTBYTES); 
#endif 
} 

static PyObject * 
whirlpool_get_name(PyObject *self, void *closure) 
{ 
#if PY_MAJOR_VERSION >= 3 
    return PyUnicode_FromStringAndSize("WHIRLPOOL", 9); 
#else 
    return PyString_FromStringAndSize("WHIRLPOOL", 9); 
#endif 
} 

static PyGetSetDef whirlpool_getseters[] = { 
    {"digest_size", (getter)whirlpool_get_digest_size, NULL, NULL, NULL}, 
    {"block_size", (getter)whirlpool_get_block_size, NULL, NULL, NULL}, 
    {"name", (getter)whirlpool_get_name, NULL, NULL, NULL}, 
    {NULL} /* sentinel */ 
}; 

static PyTypeObject Whirlpooltype = { 
    PyVarObject_HEAD_INIT(NULL, 0) 
    "whirlpool.whirlpool", /*tp_name*/ 
    sizeof(whirlpoolobject), /*tp_size*/ 
    0, /*tp_itemsize*/ 
    (destructor)whirlpool_dealloc, /*tp_dealloc*/ 
    0, /*tp_print*/ 
    0, /*tp_getattr*/ 
    0, /*tp_setattr*/ 
    0, /*tp_compare*/ 
    0, /*tp_repr*/ 
    0, /*tp_as_number*/ 
    0, /*tp_as_sequence*/ 
    0, /*tp_as_mapping*/ 
    0, /*tp_hash*/ 
    0, /*tp_call*/ 
    0, /*tp_str*/ 
    0, /*tp_getattro*/ 
    0, /*tp_setattro*/ 
    0, /*tp_as_buffer*/ 
    Py_TPFLAGS_DEFAULT, /*tp_flags*/ 
    "Whirlpool hash object", /*tp_doc*/ 
    0, /*tp_traverse*/ 
    0, /*tp_clear*/ 
    0, /*tp_richcompare*/ 
    0, /*tp_weaklistoffset*/ 
    0, /*tp_iter*/ 
    0, /*tp_iternext*/ 
    whirlpool_methods, /*tp_methods */ 
    0, /*tp_members */ 
    whirlpool_getseters, /*tp_getset */ 
}; 

/* Whirlpool functions */ 

static PyObject * 
whirlpool_new(PyObject *self, PyObject *args) 
{ 
    whirlpoolobject *wpp; 
    Py_buffer view = { 0 }; 
#if PY_MAJOR_VERSION >= 3 
    PyObject *obj = NULL; 
    if (!PyArg_ParseTuple(args, "|O:new", &obj)) 
        return NULL; 
    if (obj) 
        GET_BUFFER_VIEW_OR_ERROUT(obj, &view); 
#else 
    if (!PyArg_ParseTuple(args, "|s*:new", &view)) 
        return NULL; 
#endif 
    if ((wpp = newwhirlpoolobject()) == NULL) { 
        PyBuffer_Release(&view); 
        return NULL; 
    } 
    if (view.len > 0) { 
        NESSIEadd((unsigned char*)view.buf, Py_SAFE_DOWNCAST(view.len, Py_ssize_t, unsigned int) * 8, &wpp->whirlpool); 
    } 
    PyBuffer_Release(&view); 
    return (PyObject *)wpp; 
} 

/* List of functions exported by this module */ 

static struct PyMethodDef whirlpool_functions[] = { 
    {"new", (PyCFunction)whirlpool_new, METH_VARARGS, "Create new whirlpool object"}, 
    {NULL, NULL} /* sentinel */ 
}; 

/* Initialize this module */ 

#if PY_MAJOR_VERSION >= 3 
static struct PyModuleDef moduledef = { 
    PyModuleDef_HEAD_INIT, 
    "whirlpool", /* m_name */ 
    "Whirlpool hash algorithm implementation", /* m_doc */ 
    -1, /* m_size */ 
    whirlpool_functions, /* m_methods */ 
    NULL, /* m_reload */ 
    NULL, /* m_traverse */ 
    NULL, /* m_clear */ 
    NULL /* m_free */ 
}; 
#endif 

static PyObject * 
moduleinit(void) 
{ 
    PyObject *m, *d; 
    // CRITICAL FIX: Use Py_SET_TYPE instead of direct assignment 
    Py_SET_TYPE(&Whirlpooltype, &PyType_Type); 
    if (PyType_Ready(&Whirlpooltype) < 0) 
        return NULL; 
#if PY_MAJOR_VERSION >= 3 
    m = PyModule_Create(&moduledef); 
#else 
    m = Py_InitModule3("whirlpool", whirlpool_functions, 
                       "Whirlpool hash module"); 
#endif 
    if (m == NULL) 
        return NULL; 
    PyModule_AddIntConstant(m, "digest_size", DIGESTBYTES); 
    PyModule_AddIntConstant(m, "block_size", WBLOCKBYTES); 
    d = PyModule_GetDict(m); 
    PyDict_SetItemString(d, "WhirlpoolType", (PyObject *)&Whirlpooltype); 
    return m; 
} 

#if PY_MAJOR_VERSION >= 3 
PyMODINIT_FUNC 
PyInit_whirlpool(void) 
{ 
    return moduleinit(); 
} 
#else 
PyMODINIT_FUNC 
initwhirlpool(void) 
{ 
    moduleinit(); 
} 
#endif
