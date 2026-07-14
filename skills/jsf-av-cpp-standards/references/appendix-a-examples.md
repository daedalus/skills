APPENDIX A
AV Rule 3
Cyclomatic complexity measures the amount of decision logic in a single software module. It
may be used for two related purposes: a measure of design complexity and an aid in testing.
First, cyclomatic complexity may be utilized throughout all phases of the software lifecycle,
beginning with design, to enhance software reliability, testability, and maintainability. Second,
cyclomatic complexity aids in the test planning process by approximating the number of tests
required for a given module. Cyclomatic complexity is a structural metric based entirely on
control flow through a piece of code; it is the number of non-repeating paths through the code.
Cyclomatic complexity (v(G)) is defined for each module to be:
v(G) = e - n + 2
where n represents ‘nodes’, or computational statements, and e represents ‘edges’, or the
transfer of control between nodes.
Below is an example of source code followed by a corresponding node diagram. In the node
diagram, statements are illustrated as rectangles, decisions as triangles and transitions between
statements as lines. The number of nodes is fourteen while the number of lines connecting the
nodes is seventeen for a complexity of five.
Another means of estimating complexity is also illustrated. The number of regions bounded by
the lines, including the “infinite” region outside of the function, is generally equivalent to the
computed complexity. The illustration has 5 disjoint regions; note that it is equal to the computed
complexity.
The illustration uses a multi-way decision or switch statement. Often, a switch statement may
have many cases causing the complexity to be high, yet the code is still easy to comprehend.
Therefore, complexity limits should be set keeping in mind the ultimate goals: sensible and
maintainable code.
Example: Source Code
void compute_pay_check ( employee_ptr_type employee_ptr_IP,
check_ptr_type chk_ptr_OP )
{
//Calculate the employee’s federal, fica and state tax withholdings
1. chk_ptr_OP->gross_pay = employee_ptr_IP->base_pay;
2. chk_ptr_OP->ged_tax = federal_tax ( employee_ptr_IP->base_pay );
3. chk_ptr_OP->fica = fica ( employee_ptr_IP->base_pay );
4. chk_ptr_OP->state_tax = state_tax ( employee_ptr_IP->base_pay );
//Determine medical expense based on the employee’s HMO selection
5. if ( employee_ptr_IP->participate_HMO == true )

{
6. chk_ptr_OP->medical = med_expense_HMO;
}
else
{
7. chk_ptr_OP->medical = med_expense_non_HMO;
}
// Calc a profit share deduction based on % of employee’s gross pay
8. if (employee_ptr_IP->participate_profit_share == true )
{
9. switch( employee_ptr_IP->profit_share_plan )
{
case plan_a:
10. chk_ptr_OP->profit_share = two_percent * chk_ptr_OP->gross_pay;
break;
case plan_b:
11. chk_ptr_OP->profit_share = four_percent * chk_ptr_OP->gross_pay;
break;
case plan_c:
12. chk_ptr_OP->profit_share = six_percent * chk_ptr_OP->gross_pay;
break;
default:
break;
}
}
else
{
13. chk_ptr_OP->profit_share = zero;
}
chk_ptr_OP->net_pay = ( chk_ptr_OP->gross_pay –
chk_ptr_OP->fed_tax –
chk_ptr_OP->fica –
chk_ptr_OP->state_tax –
chk_ptr_OP->medical –
chk_ptr_OP->profit_share );
}

Example: Node Diagram
Nodes = 14
Edges = 17 true if false
Complexity = 17 - 14 + 2
= 5
6 2 7
Number of disjoint regions = 5
true if false
A switch C 13
9 3
B
5 4
10 11 12

AV Rule 11
Trigraphs can lead to confusion when question marks are used. For example, the string:
“Enter the date in the following form (??-??-????)”
would be interpreted as
“Enter the date in the following form (~~??]”
AV Rule 12
The use of digraphs listed in this rule can obscure the meaning of otherwise simple
constructs. For example,
int16 a <: 2 :> <: 2 :> = <%<%0,1%>,<%2,3%>%>;
is more simply written as
int16 a[2][2] = { {0,1}, {2,3} };
AV Rule 15
For SEAL 1/2 applications, defensive programming checks are required. Defensive
programming is the practice of evaluating potential failure modes (due to hardware failures
and/or software errors) and providing safeguards against those failure modes. For SEAL 1/2
software, System Safety is required to define all the possible software hazards (conditions in
which software could contribute to the loss of system function). If the determination is made
from the system level that hazard mitigation will be in software, then software requirements
must be derived (from the identified software hazards) to define appropriate hazard
mitigations. During coding and subsequent code inspection, the code must be evaluated to
ensure that the defensive programming techniques implied by the hazard mitigation
requirements have been implemented and comply with the requirements. Examples where
defensive programming techniques are used include (but are not limited to) management of:
• arithmetic errors—Overflow, underflow, divide-by-zero, etc. (See also AV Rule 203)
• pointer arithmetic errors—A dynamically calculated pointer references an
unreasonable memory location. (See also AV Rule 215)
• array bounds errors—An array index does not lie within the bounds of the array. (See
also AV Rule 97)
• range errors—Invalid arguments passed to functions (e.g. passing a negative value to
the sqrt() function).
Note that explicit checks may not be required in all cases, but rather some other form of
analysis may be used that achieves the same end. Consider, for example, the following use of
container a. Notice that bounds errors are not possible by construction. Hence, array-access
bounds errors are managed without explicit checks.
const uint32 n = a.size();
for (uint32 i=0 ; i<n ; ++i)
{
a[i] = i;
}

AV Rule 29
Inline functions do not require text substitutions and are well-behaved when called with
arguments (e.g. type-checking is performed).
Example: Compute the maximum of two integers.
#define max (a,b) ((a > b) ? a : b) // Wrong: macro
inline int32 maxf (int32 a, int32 b) // Correct: inline function
{
return (a > b) ? a : b;
}
y = max (++p,q); // Wrong: ++p evaluated twice
y=maxf (++p,q) // Correct: ++p evaluated once and type
// checking performed. (q is const)

AV Rule 30
Since const variables follow scope rules, are subject to type checking, and do not require text
substitutions (which can be confusing or misleading), they are preferable to macros as
illustrated in the following example.
Example:
#define max_count 100 // Wrong: no type checking
const int16 max_count = 100; // Correct: type checking may be performed
Note: Integral constants can be eliminated by optimizers, but non-integral constants will not.
Thus, in the example above, max_count will not be laid down in the resulting image.
AV Rule 32
The exception to the rule involves template class and function definitions which may be
partitioned into separate header and implementation files. In this case, the implementation
file may be included as a part of the header file. Note that the implementation file is logically
part of the header and is not separately compilable as illustrated below.
Example:
File A.h:
--------------------------------
#ifndef A_H
#define A_H
template< class T >
class A
{
public:
void do_something();
};
#include <A.cpp>
#endif
-------------------------------
File A.cpp:
-------------------------------
template< class T >
A<T>::do_something()
{
// do_something impelemtation
}
-------------------------------

AV Rule 36
Unnecessary recompilation of source files should be eliminated when possible. In the
following example, each source file includes all header files without a determination of
which ones are actually required.
Example: All header files are included in the three source files regardless of which files are
actually required. This creates several problems:
1. Inability to limit compilation scope. That is, any change to one header file means
recompiling (and consequently retesting) each source file.
2. Unnecessarily long compilation times. The repeated compilation of unnecessary
header files will significantly increase the overall compilation time.
// File 1
#include <header1.h>
#include <header2.h> // Incorrect: unneeded
#include <header3.h> // Incorrect: unneeded
… // Source for file 1
// File 2
#include <header1.h> // Incorrect: unneeded
#include <header2.h>
#include <header3.h> // Incorrect: unneeded
… // Source for file 2
// File 3
#include <header1.h> // Incorrect: unneeded
#include <header2.h> // Incorrect: unneeded
#include <header3.h>
… // Source for file 3

AV Rule 38
The header files of classes that are only referenced via pointers or references need not be
included. Doing so often increases the coupling between classes, leading to increased
compilation dependencies as well as greater maintenance efforts. Forward declarations of
the classes in question (supplied by forward headers) can be used to limit implementation
dependencies, maintenance efforts and compile times.
Example A: This example unnecessarily includes header files creating additional
dependencies in the Operator interface.
// Operator.h
#include <LM_string.h> // Incorrect: creates unnecessary dependency
#include <Date.h> // Incorrect: creates unnecessary dependency
#include <Record.h> // Incorrect: creates unnecessary dependency
class Operator
{
public:
Operator (const LM_string &name,
const Date &birthday,
const Record &flying_record);
LM_string get_name () const;
int32 get_age () const;
Record get_record () const;
…
private:
Operator_impl *impl;
};
Example B: In contrast to Example A, Example B uses forward headers to forward declare
implementation classes used by Operator. Hence the Operator interface is not dependent on
any of the implementation classes.
// Operator.h The forward headers only contain declarations.
#include <LM_string_fwd.h>
#include <Date_fwd.h>
#include <Record_fwd.h>
#include <OperatorImpl.h>
class Operator
{
public:
Operator (const LM_string &name,
const Date & birthday,
const Record &flying_record);
LM_string get_name() const;
int32 get_age () const;
record get_record () const;

…
private:
Operator_impl *impl;
};
// Operator.cc
#include <Operator.h>
#include <Operator_impl.h> // Contains implementation details of the Operator object.
…
int32 Operator::get_age()
{
impl->get_age();
}
AV Rule 39
Although header files should not contain non-const variable or function definitions in
general, inline functions and template definitions will often be included.
Example: Although definitions should, in general, be placed in .cpp files, a member function
defined inside a class declaration represents a suggestion to the compiler that the member
function should be inlined (if possible).
class Square
{
public:
float32 area() // The member function definition in the class declaration
{ // suggests to the compiler that the member function should be
return length *width; // inlined.
}
private:
float32 length;
float32 width;
};

AV Rule 40
AV Rule 40 is intended to support the one definition rule (ODR). That is, only a single
definition for each entity in a program may exist. Hence, placing the declaration of a type
(included with its definition) in a single header file ensures that duplicate definitions are
identical.
Example A: Scattering the definition of a type throughout an application (i.e. in .cpp files)
increases the likelihood of non-unique definitions (i.e. violations of the ODR).
//s.cpp
class S // Bad: S declared in .cpp file.
{ // S could be declared differently in a
int32 x; // separate .cpp file
char y;
};
Example B: Placing the definition of S in two different header files provides an opportunity
for non-unique definitions (i.e. violation of the ODR).
//s.h
class S
{
int32 x;
char y;
};
// y.h
class S // Bad: S multiply defined in two different header files.
{
int32 x;
int32 y;
};

AV Rule 42
AV Rule 42 indicates that expression-statements must be on separate lines. An expression
statement has the following form:
expression-statement:
expression ;
opt
All expressions in an expression-statement are evaluated and all side effects are completed
before the next statement is executed. The most common expression-statements are
assignments and function calls. [10]
Examples:
x = 7; y=3; // Incorrect: multiple expression statements on the same line.
a[i] = j[k]; i++; j++; // Incorrect: multiple expression statements on the same line.
a[i] = k[j]; // Correct.
i++;
j++;
Note that a for statement is a special case where condition and expression may appear on
opt opt
the same line as expression-statement[10].
iteration-statement:
while ( condition ) statement
do statement while ( expression ) ;
for ( for-init-statement condition-opt ; expression-opt ) statement
for-init-statement:
expression-statement
simple-declaration
Examples:
for( i = 0 ; i < max ; ++i) fun(); // Incorrect: multiple expression statements on the same line.
for(i = 0 ; i < max ; ++i) // Correct
{
foo();
}

AV Rule 58
Examples: The following examples illustrate the proper way to declare functions with
multiple arguments.
int32 max (int32 a, int32 b) // Correct: two parameters may appear on the
{ // same line. Order is easily understood.
…
}
// Incorrect: too many parameters on the same line.
// Difficult to document parameters in this form
msg1_in (uint16 msg_ID, float32 rate_IO, uint32 msg_size, uint16 rcv_max_instances)
{
…
}
// Correct form.
msg1_in ( uint16 msg_ID, // Unique identifier that is the label for the message
float32 rate_IO, // The desired rate for the message distributed
uint32 msg_size, // Size in bytes of the message
uint16 rcv_max_instances) // The maximum number of instances of this
// message expected in a processing frame
{
…
}
AV Rule 59
As the following examples illustrate, the bodies of if, else if, else, while, do..while and for
statements should always be enclosed within braces. As illustrated in Example A, code added
at a later time will not be part of a block unless it is enclosed by braces. Furthermore, as
illustrated by Example B, “;” can be difficult to see by itself. Hence a block (even if empty)
is required after control flow primitives.
Example A:
if (flag == 1)
{
success ();
}
else // Incorrect: log_error() was added at a later time
clean_up_resources(); // but is not part of the block (even though
log_error(); // it is at the proper indentation level).

Example B: A block, even if empty, is required after control flow primitives.
while (f(x)); // Incorrect: “;” is difficult to see.
while (f(x)) // Incorrect: “;” is difficult to see.
;
while (f(x)) // Correct
{
}
AV Rule 70
AV Rule 70 indicates that friends may be used only when a function or object requires
access to the private elements of a class, but is unable to be a member of the class for logical
or efficiency reasons. The following three examples illustrate acceptable uses of friends.
Example A: operator<<()
Consider operator<<() and operator>>() where an implicit type conversion on the left-most
argument is often required. Since an implicit type conversion on the left-most argument of a
function can only be provided through non-member functions, operator<<() and
operator>>() must be implemented as friend functions.
The preferred C++ solution is to declare such functions (that are conceptually part of the
public interface) as non-member friends of the class. This solution provides both private
element access as well as implicit type conversions.
Example B: Binary operator overloads (+, -, *, /, etc.)
Consider the example provided by Stroustrup [2]. How can a matrix-vector multiplication
operation be provided without exposing the internal representation of the matrix or the
vector? Clearly, the function requires access to the internal representation of both the matrix
and the vector. Thus, the function cannot be a member of either one. However, if the function
is not a friend, then accessors and mutators must be supplied which expose the internal
representation (i.e. violate encapsulation). Hence, adding the friend function operator*() to
the public interface of both Matrix and Vector provides a clean, encapsulated approach.
class Matrix;
class Vector
{
float32 v[4];
// …
friend Vector operator* (const matrix& m, const vector& v);
};
class Matrix {
Vector v[4];
// …
friend Vector operator*(const Matrix& m, const Vector& v);
};
Vector operator*(const Matrix& m, const Vector& v)
{

Vector r;
for (int32 i=0 ; i<4 ; i++)
{
r.v[i] = 0;
for(int32 j=0; j<4 ; j++)
{
r.v[i] += m.v[i].v[j] * v.v[j];
}
}
return r;
}
Example C: External iterators.
Since an iterator may be required to modify the contents of an object within a container
(*iterator = value ), it must be able to access the private portions of that object. Thus, if an
iterator is external to a class, it must be a friend.

AV Rule 70.1
Conceptually, developers understand that objects should not be used before they have been
created or after they have been destroyed. However, a number of scenarios may arise where
this distinction may not be obvious. Consequently, a series of examples is provided to
highlight possible areas of confusion. In many cases, the C++ standard [10] is quoted and an
explanatory code segment is provided.
Example A: Exiting main().
main() should never exit independent of the application of which it is a part. Consider the
code sample below. When main() exits, the static object destructors are invoked. Hence, the
tasks created by main() cannot depend the existence those static objects.
int32 main()
{
_main(); // Call static constructors (inserted by compiler)
// Application code begins
initialize_task_1(); // Initialize tasks
initialize_task_2();
…
initialize_task_n();
// Application code ends
__call_dtors(); // Call static destructors (inserted by compiler)
}
// Tasks begin to run. However, static objects have been destroyed.

Example B: Accessing a const Object During Construction.
Note that this scenario cannot occur without the use of global variables which are
prohibited by AV Rule 207.
During the construction of a const object, if the value of the object or any of its
subobjects is accessed through an lvalue that is not obtained, directly or indirectly, from
the constructor’s this pointer, the value of the object or subobject thus obtained is
unspecified. [10] 12.1(15)
struct C;
void no_opt(C*);
struct C
{
int c;
C() : c(0)
{
no_opt(this);
}
};
const C cobj;
void no_opt(C* cptr)
{
int i = cobj.c * 100 // value of cobj.c is unspecified
cptr->c = 1;
cout << cobj.c * 100 // value of cobj.c is unspecified
<< ’\n’;
}

Example C: Local Static Object with Non-Trivial Destructors.
If a function contains a local object of static storage duration that has been destroyed and
the function is called during the destruction of an object with static storage duration, the
program has undefined behavior if the flow of control passes through the definition of the
previously destroyed local object. [10] 3.6.3(2)
class A
{
public:
~A() { … }
};
void foo()
{
static A a; // Destructor of local static will be invoked on exit
}
class B
{
public:
~B()
{
foo(); // Destructor of static calls function with local static which may
} // already be destroyed.
};
static B B_var; // Destructor of static will be invoked on exit.

Example D: Invocation of Member Function after Lifetime of Object has Ended.
Before the lifetime of an object has started but after the storage which the object will
occupy has been allocated or, after the lifetime of an object has ended and before the
storage which the object occupied is reused or released, any pointer that refers to the
storage location where the object will be or was located may be used but only in limited
ways. …if the object will be or was of a non-POD class type, the program has undefined
behavior if:
• the pointer is used to access a non-static data member or call a non-static member
function of the object, ... [10] 3.8(5)
struct B
{
virtual void f();
void mutate();
virtual ~B();
};
struct D1 : B
{
void f()
};
struct D2 : B
{
void f()
};
void B::mutate()
{
new (this) D2; // reuses storage – ends the lifetime of *this
f(); // undefined behavior
... = this; // OK, this points to valid memory
}
// Note: placement new is only allowed in low-level memory
// management routines (see AV Rule 206).

Example E: Storage Reuse does not Require Implicit Destructor Invocation.
For an object of a class type with a non-trivial destructor, the program is not required to
call the destructor explicitly before the storage which the object occupies is reused or
released; however, if there is no explicit call to the destructor or if a delete-expression
(5.3.5) is not used to release the storage, the destructor shall not be implicitly called and
any program that depends on the side effects produced by the destructor has undefined
behavior. [8] 3.8(4)
struct A
{
~A()
{
…non-trivial destructor
}
};
struct B { … };
void c_03_06_driver()
{
A a_obj;
new (&a_obj) B(); // a_obj’s lifetime ended without calling
… // nontrivial destructor.
}
// Note: placement new is only allowed in low-level memory
// management routines (see AV Rule 206).

Example F: Object of Original Type Must Occupy Storage for Implicit Destructor
Call.
If a program ends the lifetime of an object of type T with static (3.7.1) or automatic
(3.7.2) storage duration and if T has a non-trivial destructor, the program must ensure that
an object of the original type occupies that same storage location when the implicit
destructor call takes place; otherwise the behavior of the program is undefined. This is
true even if the block is exited with an exception. [10] 3.8(8)
class T { };
struct B {
~B() { … };
};
void c_03_11_driver()
{
B b;
new (&b) T; // B’s nontrivial dtor implicitly called on memory occupied by an
// object of different type.
} //undefined behavior at block exit
// Note: placement new is only allowed in low-level memory
// management routines (see AV Rule 206).

Example G: Creating a New Object at the Storage Location of a const Object.
Creating a new object at the storage location that a const object with static or automatic
storage duration occupies or, at the storage location that such a const object used to
occupy before its lifetime ended results in undefined behavior. [10] 3.8(9)
struct B
{
B() { … };
~B() { … };
};
const B b;
void c_03_12_driver()
{
b.~B(); // A new object is created at the storage location that a const
// object used to occupy before its lifetime ended. This results
new (&b) const B; // in undefined behavior
}
// Note: placement new is only allowed in low-level memory
// management routines (see AV Rule 206).

Example H: Member Function in ctor-Initializer Invoked Before Bases are
Initialized.
If these operations (member function invocation, operand of typeid or dynamic_cast) are
performed in a ctor-initializer (or in a function called directly or indirectly from a ctor-
initializer) before all the mem-initializers for base classes have completed, the result of
the operation is undefined. [10] 12.6.2(8)
class A { public: A(int) { … }};
class B : public A
{
int j;
public:
int f() { … };
B() : A(f()), // Undefined: calls member function but base A is
// is not yet initialized
j(f()) { … } // Well-defined: bases are all initialized
};
AV Rule 71
The intent of AV Rule 71 is to prevent an object from being used before it is in a fully
initialized state. This may occur in three cases:
1. a class constructor invokes an overridden method before the derived class (supplying
the method) has been fully constructed,
2. a class constructor invokes a public or protected method that requires the object to be
fully initialized as a pre-condition of method invocation, or
3. the constructor does not fully initialize the object allowing clients access to
uninitialized data.
In the first case, C++ will not allow overridden methods to resolve to their corresponding
subclass versions since the subclass itself will not have been fully constructed and thus, by
definition, will not exist. In other words, while the base class component of a derived class is
being constructed, no methods of the derived class can be invoked through the virtual method
mechanism. Consequently, constructors should make no attempt to employ dynamic binding
in any form.
Secondly, public (and in some cases protected) methods assume object initialization and
class invariants have been established prior to invocation. Thus, invocation of such methods
during object construction risks the use of uninitialized or invalid data since class invariants
can not be guaranteed before an object is fully constructed.
Finally, the constructor should fully initialize an object (see Stroustrup [2], Appendix E and
AV Rule 72). If for some reason the constructor cannot fully initialize an object, some
provision must be made (and documented in the constructor) to ensure that clients cannot
access the uninitialized portions of the object.

AV Rule 71.1
The intent of AV Rule 71.1 is to clarify that a class’s virtual functions are resolved statically
in any of its constructors or its destructor. As a result, the placement of virtual functions in
constructors/destructors often leads to unexpected behavior.
Consider the examples below. In Example A, the virtual function does not exhibit
polymorphic behavior. In contrast, the same function is called in Example B. This time,
however, the scope resolution operator is used to clarify that the virtual function is statically
bound.
Example A:
class Base
{
public:
Base()
{
v_fun(); // Bad: virtual function called from constructor. Polymorphic
} // behavior will not be realized.
virtual void v_fun()
{
}
};
Example B:
class Base
{
public:
Base()
{
Base::v_fun(); // Good: scope resolution operator used to specify static
} // binding
virtual void v_fun()
{
}
};

AV Rule 73
A default constructor is a constructor that can be called without any arguments. Calling a
constructor without any arguments implies that objects can be created and initialized without
supplying external information from the point of call. Although this may be appropriate for
some classes of objects, there are others for which there is no reasonable means of
initialization without passing in external information. For this class of objects, the presence
of default constructors requires that additional logic be added to member functions to ensure
complete object initialization before operations are allowed to proceed. Hence, avoiding
gratuitous default constructors leads to less complex, more efficient operations on fully
initialized objects.
Consider the following examples where a Part must always have a SerialNumber. Example A
illustrates the code for a single method, getPartName(), that returns the name of the part
identified by a particular serial number. Note that additional logic must be added to the
member function getPartName() to determine if the part has been fully initialized. In
contrast, Example B does not have the unnecessary default constructor. The corresponding
implementation is cleaner, simpler, and more efficient.
Example A: Gratuitous default constructor.
class Part
{
public:
Part ()
{ serial_number =unknown;
} // Default constructor:
Part (int32 n) : serial_number(n) {}
int32 get_part_name()
{
if (serial_number == unknown) // Logic must be added to check for
{ // uninitialized state
return “”;
}
else
{
return lookup_name (serial_number);
}
private:
int32 serialNumber;
static const int32 unknown;
};
Example B: No gratuitous default constructor.
class Part
{
public:
Part (int32 n) : serial_number(n) {}
int32 get_part_name () { return lookup_name (serial_number);}
private:

int32 serial_number;
}
;
Note: The absence of a default constructor implies certain restrictions for arrays and
template-based containers of such objects. See Meyers [7] for more specific
details.
AV Rule 74
Rationale: This rule stems from the following observations:
• Member initialization is the only option for const members.
• Member initialization is the only option for reference members.
• Member initialization is never less efficient and often more efficient than assignment.
• Member initialization tends to simplify maintenance of classes.
Example A: For class Rectangle with attributes length and width, the member initialization
list should be used to initialize both attributes.
Rectangle (float32 length_, float32 width_) : length(length_), width(width_)
{
}
Example B: Suppose that length and width cannot be represented as simple expressions (e.g.
they must be read from an input stream). In this case, the member initialization list cannot be
used.
Rectangle ()
{
cin >> length >> width;
}
AV Rule 76
If an object contains a pointer to a data element, what should happen when that object is
copied? Should the pointer itself be copied and thus two different objects reference the same
data item, or should the data pointed to be copied? The default behavior is to copy the
pointer. This behavior, however, is often not the desired behavior. The solution is to define
both the copy constructor and assignment operator for such cases.
If clients should never be able to make copies of an object, then the copy constructor and the
assignment operator should be declared private (with no definition). This will prevent clients
from calling these functions as well as compilers from generating them.
Finally, a nontrivial destructor typically implies some form of resource cleanup. Hence, that
cleanup will most likely need to be performed during an assignment operation.
Note: There are some cases where the default copy and assignment operators do offer
reasonable semantics. For example, a function object holding a pointer to a member
function (e.g. std::mem_fun_t) may not require non-default behavior. For these cases,
see AV Rule 80.

AV Rule 77
A class may contain many data members as well as exist within an inheritance hierarchy.
Hence the copy constructor must copy all members (that affect the class invariant), including
those in base classes, as in the following example:
class Base
{
public:
Base (int32 x) : base_member (x) { }
Base (const Base& rhs) : base_member (rhs.base_member) {}
private:
int32 base_member;
};
class Derived : public Base
{
public:
Derived (int32 x, int32 y, int32 z) : Base (x),
derived_member_1 (y),
derived_member_2 (z) { }
Derived(const Derived& rhs) : Base(rhs),
derived_member_1 (rhs.derived_member_1),
derived_member_2 (rhs.derived_member_2) { }
private:
int32 derived_member_1;
int32 derived_member_2;
};

AV Rule 77.1
A particular ambiguity can arise with respect to compiler-supplied, implicit copy constructors
as noted in [10] 12.8(4):
If the class definition does not explicitly declare a copy constructor, one is declared implicitly.
Thus, for the class definition
struct X {
X(const X&, int);
};
a copy constructor is implicitly-declared. If the user-declared constructor is later defined as
X::X(const X& x, int i =0) { /* ... */ }
then any use of X’s copy constructor is ill-formed because of the ambiguity; no diagnostic
is required.

AV Rule 79
Releasing resources in a destructor provides a convenient means of resource management,
especially in regards to exceptional cases. Moreover, if it is possible that a resource could be
leaked, then that resource should be wrapped in a class whose destructor automatically cleans
up the resource.
Example A: Stroustrup [2] provides an example based on a file handle. Note that the
constructor opens the file while the destructor closes the file. Any
possibility that a client may “forget” to cleanup the resource is eliminated.
class File_ptr // Raw file pointer wrapped in class to ensure
{ // resources are not leaked.
public:
File_ptr (const char *n, const char * a) { p = fopen(n,a); }
File_ptr (FILE* pp) { p = pp; }
~File_ptr ()
{
if (p)
{
fclose(p)
};
} // Clean up file handle.
…
private:
FILE *p;
};
use_file (const char *file_name)
{ // Client does not have to remember to clean up file handle
File_ptr f(fn,”r”); // (impossible to leak file handles).
// use f
} // f goes out of scope so the destructor is called,
// cleaning up the file handle.

AV Rule 81
Self-assignment must be handled appropriately by the assignment operator. Example A
illustrates a potential problem, whereas Example B illustrates an acceptable approach.
Example A: Although it is not necessary to check for self-assignment in all cases, the
following example illustrates a context where it would be appropriate.
Base &operator= (const Base &rhs)
{
release_handle (my_handle); // Error: the resource referenced by myHandle is
my_handle = rhs.myHandle; // erroneously released in the self-assignment case.
return *this;
}
Example B: One means of handling self-assignment is to check for self-assignment before
further processing continues as illustrated below.
Base &operator= (const Base& rhs)
{
if (this != &rhs) // Check for self assignment before continuing.
{
release_handle(my_handle); // Release resource.
my_handle = rhs.my_handle; // Assign members (only one member in class).
}
else
{
}
return *this;
}

AV Rule 83
A class may contain many data members as well as exist within an inheritance hierarchy.
Hence the assignment operator must assign all members, including those in base classes,
which affect the class invariant as in the following example:
Note: Definition of operator=() is included in the class declaration to simplify the
explanation of this rule. It breaks the “no function definition in class declaration”
rule.
class Base
{
public:
Base (int32 x) : base_member (x) {}
Base &operator=(const Base& rhs)
{
if (this != &rhs) // Check for self assignment before continuing.
{
base_member = rhs.base_member; // Assign members (only one member in class).
}
else
{
}
return *this;
}
private:
int32 base_member;
};
class Derived : public Base
{
public:
Derived (int32 x, int32 y, int32 z) : Base (x),
derived_member_1 (y),
derived_member_2 (z) {}
Derived& operator=(const Derived& rhs)
{
if (this != &rhs) // Check for self-assignment
{
Base::operator=(rhs); // Copy base class elements.
derived_member_1 = rhs.derived_member_1; // Assign all members of derived class
derived_member_2 = rhs.derived_member_2;
}
else
{
}
return *this;
}

private:
int32 derived_member_1;
int32 derived_member_2;
};
AV Rule 85
The following example illustrates how operator!=() may be defined in terms of
operator==(). This construction simplifies maintenance.
bool operator==(Sometype a)
{
if ( (a.attribute_1 == attribute_1) &&
(a.attribute_2 == attribute_2) &&
(a.attribute_3 == attribute_3) &&
...
(a.attribute_n == attribute_n) )
{
return true;
}
else
{
return false;
}
bool operator!=(Some_type a)
{
return !(*this==a); //Note “!=” is defined in terms of "=="
}

AV Rule 87
Hierarchies based on abstract classes are preferred. Therefore the hierarchies at the top of the
diagram are preferred over the hierarchy at the bottom of the diagram.
Users
Users Interface
Interface
Impl Impl
Abstract class
hierarchies
D1 D2 D1 D2
Users
Hierarchies based on abstract
Base
Interface classes are preferred.
& Data
Non abstract
class hierarchy
D1 D2 Public inheritance
Private/protected
inheritance

AV Rule 88
In the context of this rule, an interface is specified by a class which has the following
properties:
• it is intended to be an interface,
• its public methods are pure virtual functions, and
• it does not hold any data, unless those data items are small and function as part of the
interface (e.g. a unique object identifier).
Note 1: Protected members may be used in a class as long as that class does not
participate in a client interface.
Note 2: Classes with additional state information may be used as bases provided
composition is performed in a disciplined manner with templates (e.g. policy-
based design). See the “Programming with Policies” paragraph below.
The following diagrams illustrate both good and bad examples of multiple inheritance.
interface interface implementation implementation implementation
class class
Public inheritance
derived Private/protected
class inheritance
Private inheritance
Users Implementers
Good: Two interfaces, two private implementations,
and one protected implementation.
1 2 3 n 1
interface interface interface interface implementation
class class class … class
Public inheritance
derived Private/protected
class inheritance
Users Implementers
Good: n interfaces and one protected implementation.

interface Impl
class
Users
interface D1 Public inheritance
class
Protected/private
inheritance
Private inheritance
D2 Implementers
Good: D1 has one interface and one implementation.
D2 has two interfaces and one implementation.
Impl interface
class
Implementers Users
Impl D1
Public inheritance
Protected/private
inheritance
Private inheritance
D2
Good: Both D1 and D2 have one interface and one
implementation.

Virtual base classes: The following diagram illustrates the difference between virtual and
non-virtual base classes. The subsequent diagram illustrates legitimate uses of virtual base
classes.
class Base {…}; class Base {…};
class Der1 : public Base {…}; class Der1 : public virtual Base {…};
class Der2 : public Base {…}; class Der2 : public virtual Base {…};
class Join : public Der1, public Der2 {…}; class Join : public Der1, public Der2 {…};
Base Base Base
Non-virtual Virtual base
bases
Der1 Der2 Der1 Der2
Join Join

Users Users
Interface
Interface 1 Shared Interface 2
Impl
(data)
Der1 Der2
Der1 Der2
Implementers
Join
Join
Public inheritance
Private/protected
inheritance
Good: Both hierarchies are acceptable. Note the
Implementation class in the right hierarchy
should not be directly used by clients.

Protected data in class interface: As previously mentioned, protected data may be used in a
class as long as that class does not participate in a client interface. The following diagram
illustrates this point.
Users Protected data
Interface
& data
Public inheritance
Private/protected
inheritance
D1 D2 D3
Bad: Derived classes (D1, D2, or D3) may hijack
the base class invariant since they have access
to the base class protected data.
Protected data
Shared
Impl
Public inheritance
Private/protected
inheritance
Users
D1 D2 D3
Good: The base class is an implementation class. Non-public inheritance prevents
derived classes from being implicitly converted to the base class type. Hence users
may only manipulate the derived classes through the derived class interfaces.

Policy-based Design
As previously mentioned, classes with additional state information may be used as bases
provided composition is performed in a disciplined manner with templates (e.g. policy-based
design). A form of programming that is used when classes must be customizable but
efficiency is paramount is called policy programming. When a class’ functionality can be
separated into a set of independent concerns and each concern can be programmed in more
than one way, policy programming is very useful. In particular, it simplifies maintenance by
avoiding replication of code. A classic example is a matrix math package. The concerns are
as follows:
• Access – how are the elements laid out in memory? Some possibilities are row
major, column major, and upper triangular.
• Allocation – from where does the memory come? Some possibilities are the system
heap, a fixed area, or allocated by a user-specified allocation scheme.
• Error Handling – what is done when an error occurs? Some possibilities are to throw
an exception, log an error message, set an error code, or restart the process.
These concerns are independent of one another and can be coded separately. For example:
template< class T >
class Row_major
{
public:
typedef T value_type;
Row_major( int32 nrows, int32 ncols, T* array ) :
nrows_(nrows), ncols_(ncols), array_(array)
{}
~Row_major() {}
int32 size1() const { return nrows_; }
int32 size2() const { return ncols_; }
const T& operator() ( int32 i, int32 j ) const { return array_[i*ncols_+j]; }
T& operator() ( int32 i, int32 j ) { return array_[i*ncols_+j]; }
private:
int32 nrows_;
int32 ncols_;
T* array_;
};
The class Column_major would be very similar except that the parenthesis operator would
return array_[j*nrows_+i].
Rather than create code for each possible combination of concerns, we create a template class
that brings together implementations for each concern. Thus, assuming that:
• Access defines the parenthesis operator,
• Alloc defines the template method
T* allocate<T>( int32 n ) , and
• Err defines the following methods

void handle_error( int32 code, int32 nr, int32 nc )
void handle_error( int32 code, int32 i, int32 j, int32 nr, int32 nc )
we can compose the Matrix class as follows:
template< class Access, class Alloc, class Err >
class Matrix : public Access, Alloc, Err // Alloc and Err are private bases
{
Matrix( int32 nrows, int32 ncols ) :
Access(nrows,ncols,allocate<T>(nrows*ncols))
{
if( array_==0 )
{
handle_error( Err::allocation_failed, nrows, ncols );
}
}
Access::value_type& at( int32 i, int32 j )
{
if( i<0 || i>nrows_ || j<0 || j>ncols_ )
{
handle_error( Err::index_out_of_bounds, i, j, nrows_, ncols_ );
i = j = 0;
}
return this->operator()(i,j);
}
// and so on...
};
Thus, the Matrix class brings all the policies together into a functional class. Users may
create
• Matrix< Row_major, Heap, Exceptions > or
• Matrix< Lower_triangular, Pool_allocation, Restart >
as dictated by their needs.
Note that the Matrix class could have been written where Access, Alloc, and Err exist as data
members of Matrix rather than deriving from it. This technique has several drawbacks including
the necessity of creating (and maintaining) a large number of forwarding functions as well as
inferior performance characteristics.

AV Rule 88.1
Stateful virtual bases should be rarely used and only after other design options have been
carefully weighed. Stateful virtual bases do introduce a concern with respect to non-exclusive
access to shared data. However, this concern is not unique to stateful virtual bases. On the
contrary, it is present in any form of aliasing. For example, two pointers that point to a single
data object suffer from the same condition, but this situation is arguably worse since there are
no declarations in the system to highlight this form of aliasing (as there are for virtual bases).
Stateful virtual bases are theoretically important since they provide the only explicit means of
sharing data within a class hierarchy without transitioning to a brittle, single-rooted hierarchy
employing stateful bases. The other alternative is simpler and uglier yet: give each class that
needs access to shared data a pointer to (1) a part of the object or to (2) a separate object -
thus "simulating" a virtual base. In essence, a stateful virtual base should be used only to
avoid the implicit sharing of data via pointers or references.
Consider the following hierarchy:
A
/ \
B C
| |
D E
\ /
F
AV Rule 88.1 would make the fact that A is a virtual base explicit not only in the declarations
of B and C, but also in the declarations of D, E, and F (assuming D, E, and F all access A):
struct A {};
struct B : virtual A {};
struct C : virtual A {};
struct D : B, virtual A {};
struct E : C, virtual A {};
struct F : D, E, virtual A {};
Consequently, the sharing of data is explicitly documented. The alternative:
struct A {};
struct B : virtual A {};
struct C : virtual A {};
struct D : B {}; // Violation of 88.1
struct E : C {}; // Violation of 88.1
struct F : D, E {}; // Violation of 88.1
can be obscure. That is, it is not obvious that D and E do not have exclusive access to A.

AV Rule 92
AV Rule 92 specifies that subtypes should conform to the Liskov Substitution Principle
(LSP) which states:
…for each object o of type S there is an object o of type T such that for all
1 2
programs P defined in terms of T, the behavior of P is unchanged when o is
substituted for o then S is a subtype of T [5].
More simply put, the LSP suggests that a pointer or reference to a derived type may be
substituted anywhere one of its base types is used without the context being aware of the
substitution. Following this important principle will ensure that functions/modules can be
constructed without requiring the context of a base class to be aware of all current and future
derivatives of that base class. In other words, class hierarchies may be constructed so that
new extensions/specializations will not break or yield surprise results when used in existing
applications.
For example, should Penguin be derived from the base class, Bird, that contains the fly()
operation? The precondition (all birds can fly) for the base class, Bird, is stronger than the
precondition (I can’t fly) of the derived class, Penguin. Hence, Penguin is not a subtype of
Bird, and therefore should not be publicly derived from Bird.
AV Rule 93
Example A illustrates the class Person that is constructed with members Name, Address, and
PhoneNumber. Hence, the functionality of Person is implemented in terms of the member
elements (Name, Address, and PhoneNumber).
Example A:
class Person
{
private:
string name; // Person is composed of members Name, Address, and
// PhoneNumber
string address;
string phone_number;
…
};
In general, membership should be used except where access to protected members or virtual
methods is required. In these situations, membership will not work. Instead, non-public
inheritance should be used. Consider the GenericStack example provided by Meyers [6], item
43. One may reuse the GenericStack implementation for stacks of any type as illustrated in
Example B. Note, however, that the GenericStack implementation is “too dangerous” to be
used by it self. Instead, type-safe interfaces are supplied through a template class. The
GenericStack’s methods are declared protected to prevent the use of this class in isolation
from a type-safe interface. As a result, derived classes must make use of GenericStack’s
protected members via inheritance rather than class membership.

Example B:
class Generic_stack
{
protected: // Methods are protected so that Generic_stack
// cannot be used by itself.
Generic_stack();
~Generic_stack();
void push (void *object);
void * pop (void);
bool empty () const;
private:
…
};
A type-safe interface for GenericStack may be implemented as:
template<class T>
class Stack: private Generic_stack // Reuse base class implementation
{
public:
void push (T *object_ptr) { GenericStack::push (object_ptr); }
T * pop (void) { return static_cast<T*>(Generic_stack::pop()); }
bool empty () const { return Generic_stack::empty(); }
};

AV Rule 94
Nonvirtual functions are statically bound. In essence, a nonvirtual function will hide its
corresponding base class version. Hence a single derived class object may behave either as a
base class object or as a derived class object depending on the way in which it was
accessed—either through a base class pointer/reference or a derived class pointer/reference.
To avoid this duality in behavior, nonvirtual functions should never be redefined.
Example:
class Base
{
public:
mf (void);
};
class Derived : public Base
{
public:
mf (void);
};
example_function(void)
{
Derived derived;
Base* base_ptr = &derived; // Points to derived
Derived* derived_ptr = &derived; // Points to derived
base_ptr->mf(); // Calls Base::mf() *** Different behavior for same object!!
derived_ptr->mf(); // Calls Derived::mf()
}

AV Rule 95
While C++ dynamically binds virtual methods, the default parameters of those methods are
statically bound. Hence, the draw() method of the derived type (Circle), if referenced through
a base type pointer (Shape *), will be invoked with the default parameters of the base type
(Shape).
Example A:
enum Shape_color { red, green, blue };
class Shape
{
public:
virtual void draw (Shape_color color = green) const;
…
}
class Circle : public Shape
{
public:
virtual void draw (Shape_color color = red) const;
…
}
void fun()
{
Shape* sp;
sp = new Circle;
sp->draw (); // Invokes Circle::draw(green) even though the default
} // parameter for Circle is red.

AV Rule 101 and AV Rule 102
Since many template instantiations may be generated, the compiler should be configured to
provide a list of actual instantiations for review and testing purposes. The following table
illustrates the output of a Stack class that was instantiated for both float32 and int32 types.
Note that the method instantiations are listed so that a complete test plan may be constructed.
Template Parameter Type Library/Module
Stack<T1>::Stack<float32>(int) [with T1=float32] shape_hierarchy.a(shape_main.o)
Stack<T1>::Stack<int32>(int) [with T1=int32] shape_hierarchy.a(shape_main.o)
T1 Stack<T1>::pop() [with T1=float32] shape_hierarchy.a(shape_main.o)
T1 Stack<T1>::pop() [with T1=int32] shape_hierarchy.a(shape_main.o)
void Stack<T1>::push(T1) [with T1=float32] shape_hierarchy.a(shape_main.o)
void Stack<T1>::push(T1) [with T1=int32] shape_hierarchy.a(shape_main.o)

AV Rule 103
Stroustrup [4] provides a solution (for creating template parameter constraints) that requires
minimal effort, requires no additional code to be generated, and causes compilers to produce
acceptable error messages (including the word constraint).
Moreover, Stroustrup provides the following sample constraints that check the ability of
template parameters to engage in derivations, assignments, comparisons and multiplications.
(Note that the following elements are good candidates for a constraints library.)
template<class T, class B> struct Derived_from {
static void constraints(T* p) { B* pb = p; }
Derived_from() { void(*p)(T*) = constraints; }
};
template<class T1, class T2> struct Can_copy {
static void constraints(T1 a, T2 b) { T2 c = a; b = a; }
Can_copy() { void(*p)(T1,T2) = constraints; }
};
template<class T1, class T2 = T1> struct Can_compare {
static void constraints(T1 a, T2 b) { a==b; a!=b; a<b; }
Can_compare() { void(*p)(T1,T2) = constraints; }
};
template<class T1, class T2, class T3 = T1> struct Can_multiply {
static void constraints(T1 a, T2 b, T3 c) { c = a*b; }
Can_multiply() { void(*p)(T1,T2,T3) = constraints; }
};
Thus, given the Can_copy constraint above, a draw_all() function may be written that
asserts, at compile time, that only containers comprised of pointers to Shape or pointers to a
classes publicly derived from Shape (or convertible to Shape) may be passed in.
template<class Container>
void draw_all(Container& c)
{
typedef typename Container::value_type T;
Can_copy<T,Shape*>(); // accept containers of only Shape*’s
for_each(c.begin(),c.end(),mem_fun(&Shape::draw));
}
Additional constraints may be easily created. See [4] for further information concerning
constraint creation and use.

AV Rule 108
The following example illustrates a case where function overloading or parameter defaults
may be used instead of an unspecified number of arguments.
Example A: Consider a function to compute the length of two, three, or four dimensional
vectors. A variable argument list could be used, but introduces unnecessary complexities.
Alternatively, function overloading or parameter defaulting provide much better solutions.
// Unspecified number of arguments
float32 vector_length (float32 x, float32 y, …); // Error prone
// Function overloading
float32 vector_length (float32 x, float32 y);
float32 vector_length (float32 x, float32 y, float32 z);
float32 vector_length (float32 x, float32 y, float32, z, float32 w);
// Default parameters
float32 vector_length (float32 x, float32 y, float32 z=0, float32 w=0);
AV Rule 109
In the following example, Square declares two functions area() and morph(). Since the
designer wants to inline the relatively simple method area(), it is defined within the class
specification. In contrast, there is no intent to inline the complex method morph(). Hence
only the method declaration is included.
class Square : public Shape
{
public:
float32 area()
{
return length*width;
} // area() will be inlined since it is defined
// in the class specification.
morph (Shape &s); // morph() is not intended to be inlined so its
}; // implementation is contained in a separate file.

AV Rule 112
The following examples illustrate several ways in which function return values can obscure
resource ownership and hence risk resource leakage. Note in the following examples, new
need not allocate memory from the heap, but could be overloaded on the class in question.
Example A: Returning a dereferenced pointer initialized by new is error prone since the
caller must remember to delete the object. This becomes more difficult if that object happens
to be a temporary object.
X& f (float32 a)
{
return *new x(a); // Error prone. Caller must remember to perform
} // the delete.
X& ref = f(1); // The caller of f() must be responsible for deleting
… // the memory.
delete &ref // delete must be called for every invocation of f().
…
X& x = f(1)*f(2)*f(3)*f(4); // Memory leak: delete not called for temporaries.
Example B: Returning a pointer to a local object is problematic since the object ceases to
exist after return. AV Rule 111 explicitly prohibited this practice.
X* f (float32 a) // Error: the caller most likely believes he is
{ // responsible for deleting the object. However, the object
X b(a); // ceases to exist when the function returns.
return &b
}
Example C: A function can return a pointer to an object, but the recipient must remember to
perform the delete.
X *f(float32 a)
{
return new X(a); // Beware of leak: recipient must remember to perform the delete.
}
Example D: Returning an object by value is a simple method that does not obscure
ownership issues.
X f(float 32 a) // Simple and clear.
{
X b(a);
return b;
}

AV Rule 120
Overloading functions can be a powerful tool for creating families of related operations that
differ only with respect to argument type. If not used consistently, however, overloading can
lead to considerable confusion.
Example A: Proper usage of function overloading is illustrated below. All overloads of
contains() share the same name as well as perform the same conceptual task.
class String
{
public: // Used like this:
// ... // String x = "abc123";
int32 contains ( const char c ); // int32 i = x.contains( 'b' );
int32 contains ( const char* cs ); // int32 j = x.contains( "bc1" );
int32 contains ( const String& s ); // int32 k = x.contains( x );
// ...
};
Example B: Improper use of operator overloading is illustrated below. For two-dimensional
vectors, operator*() means dot product while for three dimensional vectors, operator*()
means cross product.
Vector2d {
public:
float32 operator*(const Vector2d & v); // compute dot product
…
};
Vector3d {
public:
Vector3d operator*(const Vector3d & v) // compute cross product
…
};

AV Rule 121
The Green Hills compiler employs two inlining approaches, each using a different inlining
strategy, and each coming at a different stage. The first is a front-end inliner. It will only
consider inline functions (functions declared with the keyword inline or member functions
whose bodies are defined inside class definitions).
The front-end inliner will inline only those functions which can be converted to expressions.
Therefore, functions which simply return an expression, straight code functions (which can
be converted to comma expressions), or functions with if statements that can be converted to
“?:” expressions will be considered candidates for inlining. The front-end inliner is not
capable of inlining more complex statements (e.g. functions containing loops).
The second inliner is the independent code inliner which is capable of inlining most any
function (except recursive functions). Inlining complex functions may lead to significant
code bloat as well as to complicate debugging efforts. As a result, only the front-end inliner
should be used in C/C++ programs.
AV Rule 122
The following example illustrates a class that inlines a trivial accessor and a trivial mutator.
class Example_class
{
public:
int32 get_limit (void) // Sample accessor to be inlined
{
return limit;
}
void set_limit (int32 limit_parm) // Sample mutator to be inlined
{
limit = limit_parm;
}
private:
int32 limit;
};

AV Rule 124
Simple forwarding functions should be inlined as illustrated below.
Example A:
inline draw() // Example of a forwarding function that should be inlined
{
draw_foreground ();
}
AV Rule 125
The construction of large or complex temporary objects can exact a significant performance
penalty. Consequently, the following observations are provided as guidance in limiting the
number unnecessary temporaries.
• Problem 1: Temporary objects are created (and destroyed) to make function calls
succeed via implicit type conversions. The conversions will occur either when an
argument is passed by value or is passed as a reference to const objects.
• Solution 1: Overload the function in question so that the implicit conversion will not
be necessary.
• Problem 2: Temporary objects are created (and destroyed) when a function returns
an object.
• Solution 2a: Return a reference when possible. If it is not possible to return a
reference (as in the case of overloading operator*()), try to take advantage of “return
value optimization” (eliminating a local temporary by utilizing the object at the
functions return site). For example:
c = a * b;
…
inline const Rational operator*(const Rational& lhs,
const Rational& rhs)
{
return Rational (lhs.get_numerator() * rhs.get_numerator(),
lhs.get_denominator() * rhs.get_denominator());
}
Eliminates both the temporary created inside the operation*() and the temporary
returned by operator*(). The new object is simply constructed inside the space
allocated for “c”.
• Solution 2b: Change the design. For example, use operator*=() instead of
operator*(), since operator*= () does not require the generation of a temporary as
does operator*().

AV Rule 126
A C++ style comment begins with “//” and terminates with a new-line. However, the
placement of vertical-tab or form-feed characters within a comment may produce unexpected
results. That is, if a form-feed or a vertical-tab character occurs in a C++ style comment, only
white-space characters may appear between it and the new-line that terminates the comment.
An implementation is not required to diagnose a violation of this rule. [10]
AV Rule 136
The following code illustrates some problems encountered when a variable is not declared at
the smallest feasible scope.
void fun_1()
{
int32 i; // Bad: i is prematurely declared (the intent is to use i in the
// for loop only)
… // Bad: i has a meaningless value in the region of the code
for (i=0 ; i<max ; ++i)
{
…
}
…. // Bad: i should not be used here, but could be used anyway
for(int32 j=0 ; j<max ; ++j) // Good: j is not declared or initialized until needed
{ // Good: j is only known within the for loop’s scope
…
}
}
AV Rule 137
MISRA Reason: Declarations at file scope are external by default. Therefore if two files
both declare an identifier with the same name at file scope, the linker will either give an
error, or they will be the same variable, which may not be what the programmer intended.
This is also true if one of the variables is in a library somewhere. Use of the static storage-
class specifier will ensure that identifiers are only visible to the file in which they are
declared.
If a variable is only to be used by functions within the same file then use static. Similarly if a
function is only called from elsewhere within the same file, use static.
Typically, functions whose declarations appear in a header (.h) file are intended to be called
from other files and should therefore never be specified with the static keyword. Conversely,
functions whose declarations appear in an implementation body (.cpp) file should never be
called from other files, and hence should always be declared with the static keyword.

AV Rule 138
The C++ Standard [10] defines linkage in the following way:
• When a name has external linkage, the entity it denotes can be referred to by names
from scopes of other translation units or from other scopes of the same translation
unit.
• When a name has internal linkage, the entity it denotes can be referred to by names
from other scopes in the same translation unit.
Hence, having names with both internal and external linkage can be confusing since the
objects to which they actually refer may not be obvious. Consider the following example
where the i declared on line 1 has internal linkage while the i on line 2 has external linkage.
Which entity is referenced by the i on line 3?
{
static int32 i=1; // line 1
{ // Bad: the i with external linkage hides the i
// with internal linkage.
extern int32 i; // line 2
…
a[i] = 10; // line 3: Confusing: which i?
}
}
AV Rule 139
Adherence to this rule will normally mean declaring external objects in header files which
will then be included in all those files that use those objects (including the files which define
the objects).
Example A: Two files declare the same variable. This style could lead to errors since a
could be declared in many different files. A change in one of those files
would affect all others and would be difficult to pinpoint.
// In File_1.cpp
int32 a = 3;
// In File_2.cpp
extern int32 a;

Example B: Here, a is declared in a header file. All other files that need access to a
simply include the header file. In this way, consistency is assured.
// In File_1.h
extern int32 a;
// In File_1.cpp
#include <File_1.h>
int32 a = 3;
// In File_2.cpp
#include <File_1.h>
AV Rule 141
Example A: Declaring an enumeration in the definition of its type can lead to readability
problems and unnamed data types as illustrated below.
enum // Don’t do this: Creates an unnamed data type.
{
up,
down
} direction;
enum i { in, out } i; // Don’t do this: Difficult to read.
Example B: Separation of the declaration and definition are preferred as illustrated below.
Note that this requires the data type to be named which provides a mechanism to create other
variables of the same type and the ability to type cast.
enum XYZ_direction
{
up,
down
};
XYZ_direction direction;
Example C: Note that a legitimate use of an unnamed enumeration is to define symbolic
constants within a class declaration.
class X
{
enum
{
max_length = 100,
max_time = 73
}; // Defines symbolic constants for the class
…
};

Example D: Note that the following declarations are not prohibited under this rule.
int32 i=0;
pair<float32,int32> p;
AV Rule 142
MISRA Rule 30 requires all automatic variables to have an assigned value. Compilers will,
by default, initialize external and static variables to the value zero. However, it is considered
good practice to initialize all variables, not just automatic/stack variables, to an initial value
for purposes of 1) clarity and 2) bringing focused attention to the initialization of each
variable. Therefore, this rule requires ALL variables to be initialized. Exception may be
granted for volatile variables.
AV Rule 143
Introducing variables before they can be assigned meaningful values causes a number of
problems as illustrated in the following examples.
Example A: The following code illustrates some problems encountered when variables are
introduced before they can be properly initialized.
void fun_1() // Poor implementation
{
int32 i; // Bad: i is prematurely declared (the intent is to use i in the for
// loop only)
int32 max=0; // Bad: max initialized with a dummy value.
… // Bad: i and max have meaningless values in this
// region of the code.
max = f(x);
for (i=0 ; i<max ; ++i)
{
…
}
…. // Bad: i should not be used here, but could be used anyway
}
void fun_1() // Good implementation
{
….
int32 max = f(x); // Good: max not introduced until meaningful value is
// available
for (int32 i=0 ; i<max ; ++i) // Good: i is not declared or initialized until needed
{ // Good: i is only known within the for loop’s scope
…
}
}

Example B: An instance of class X is constructed prior to the point at which it can be fully
initialized. To complete the initialization, a separate init() method must be called when
sufficient information becomes available. However, since the object may only be in a quasi-
valid state prior to the invocation of init(), all method invocations between object
construction and init() are suspect. See also AV Rule 73 concerning unnecessary default
constructors.
class X {
public:
X::X() {} // Bad: default constructor builds partially initialized object.
init (int32 max_, int32 min_)
{
max = _max ;
min = _min;
}
int32 range()
{
return max-min ;
}
…
private:
int32 max;
int32 min;
};
void foo()
{
X x; // Bad: x constructed but without data
…
x.range(); // Bad: undefined result.
….
x.init(lbound, ubound); // Bad: x initialized later than necessary
}

AV Rule 145
If an enumerator list is given with no explicit initialization of members, then C++ allocates a
sequence of integers starting at 0 for the first element and increasing by 1 for each
subsequent element. For most purposes this will be adequate.
An explicit initialization of the first element, as permitted by the above rule, forces the
allocation of integers to start at the given value. When adopting this approach it is essential to
ensure that the initialization value used is small enough that no subsequent value in the list
will exceed the int storage used by enumeration constants.
Explicit initialization of all items in the list, which is also permissible, prevents the mixing of
automatic and manual allocation, which is error prone. However it is then the responsibility
of the programmer to ensure that all values are in the required range, and that values are not
unintentionally duplicated.
Example A:
//Legal enumerated list using compiler-assigned enum values
//off=0, green=1, yellow=2, red=3
enum Signal_light_states_type
{
off,
green,
yellow,
red
};
Example 2:
// Legal enumeration, assigning a value to the first item in the list.
enum Channel_assigned_type
{
channel_unassigned = -1,
channel_a,
channel_b,
channel_c
};

Example 3:
// Control mask enumerated list. All items explicitly
// initialized.
enum FSM_a_to_d_control_enum_type
{
start_conversion = 0x01,
stop_conversion = 0x02,
start_list = 0x04,
end_list = 0x08,
reserved_3_bit = 0x70,
reset_device = 0x80
};
Example 4:
// Legal: standard convention used for enumerations that are intended to index arrays.
enum Color {
red,
orange,
yellow,
green,
blue,
indigo,
violet,
Color_begin = red,
Color_end = violet,
Color_NOE // Number of elements in array
};
AV Rule 147
Manipulating the underlying bit representation of a floating point number is error-prone, as
representations may vary from compiler to compiler, and platform to platform. There are,
however, specific built-in operators and functions that may be used to extract the mantissa
and exponent of floating point values.

AV Rule 151.1
Since string literals are constant, they should only be assigned to constant pointers as
indicated below:
char* c1 = “Hello”; // Bad: assigned to non-const
char c2[] = “Hello”; // Bad: assigned to non-const
char c3[6] = “Hello”; // Bad: assigned to non-const
c1[3] = ‘a’; // Undefined (but compiles)
const char* c1 = “Hello”; // Good
const char c2[] = “Hello”; // Good
const char c3[6] = “Hello”; // Good
c1[3] = ‘a’; // Compile error
AV Rule 157
Care should be taken when short-circuit operators are utilized. For example, if the logical
expression in the following code evaluates to false, the variable x will not be incremented.
This could be problematic since subsequent statements may assume that x has been
incremented.
if ( logical_expression && ++x) // Bad: right-hand side not evaluated if the logical
// expression is false.
…
f(x); // Error: Assumes x is always incremented.
…
AV Rule 158
The intent of this rule is to require parenthesis where clarity will be enhanced while stopping
short of over-parenthesizing expressions. In the following examples, parenthesizing operands
(that contain binary operators) of the logical operators && or || enhances readability.
Examples:
valid (p) && add(p) // parenthesis not required
x.flag && y.flag // parenthesis not required
a[i] || b[j] // parenthesis not required
(x < max ) && (x > min) // parenthesis required
(a || b) && (c || d) // parenthesis required

AV Rule 160
The intent of this rule is to prohibit assignments in contexts that are obscure or otherwise
easily misunderstood. The following example illustrates some of the problems this rule
addresses.
Note that a for-init-statement (that is not a declaration) is an expression statement.
for ( for-init-statement condition-opt ; expression-opt ) statement
for-init-statement:
expression-statement
simple-declaration
Examples:
x = y; // Good: the intent to assign y to x and then check if x is
if (x != 0) // not zero is explicitly stated.
{
foo ();
}
if ( ( x = y) != 0 ) // Bad: not as readable as it could be.
{ // Assignment should be performed prior to the “if”statement
foo ();
}
if (x = y) // Bad: intent is very obscure: a code reviewer could easily
{ // think that “==” was intended instead of “=”.
foo ();
}
for (i=0 ; i<max ; ++i) // Good: assignment in expression statement of “for” statement
{
…
}
AV Rule 168
MISRA Rule 42 only allows use of the comma operator in the control expression of a for
loop. The comma operator can be used to create confusing expressions. It can be used to
exchange the values of variable array elements where the exchange appears to be a single
operation. This simplicity of operation makes the code less intuitive and less readable. The
comma operator may also be easily confused with a semicolon used in the for loop syntax.
Therefore, all uses of the comma operator will not be allowed.

AV Rule 177
User-defined conversion functions come in two forms: single-argument constructors and type
conversion operators. Implicit type conversions may be eliminated as follows:
• Single-argument constructors: use the “explicit” keyword on single-argument
constructors so that the compiler will not supply implicit conversions through the
constructor.
• Type conversion operators: don’t define conversion operators. If type conversion
functionality is required, then define a member function to fulfill the same role.
Unlike the type conversion operator, however, a member function must be called
explicitly, thus eliminating any “surprises” that could arise if the type conversion
operator were used.
Examples 1 and 2 demonstrate these principles.
Example 1a: The Vector_int class below has a single argument constructor used to build
vectors. However, this constructor may be called in ways a user may not expect. The solution
is to use the explicit keyword in the constructor declaration which precludes the constructor
from being called implicitly.
bool operator == (const Vector_int &lhs, const Vector_int &rhs)
{
// compare two Vector_ints
}
class Vector_int {
public:
Vector_int (int32 n);
…
};
Vector_int v1(10),
v2(10); // create two vectors of size 10;
…
for (int32 i=0 ; i<10 ; ++i)
{
if (v1 == v2[i]) // The programmer meant to compare the elements of two Vectors.
{ // However, the subscript of the first was inadvertently left off.
… // Thus, the compiler is asked to compare a Vector_int with an
} // integer. The single argument constructor is called to convert the
} // integer to a new Vector_int so that the comparison can take place.
// This is almost certainly not what is expected.

Example 1b: The constructor is declared explicit so that the error is caught at compile time.
class Vector_int
{
public:
explicit Vector_int (int32 n) ;
…
};
Vector_int v1(10), v2(10); // create two vectors of size 10;
…
for (int32 i=0 ; i<10 ; ++i)
{
if (v1 == v2[i]) // The programmer meant to compare the elements of two Vectors.
{ // However, the subscript of the first was inadvertently left off.
… // Thus, the compiler is asked to compare a Vector_int with an
} // integer. The explicit keyword prevents the constructor from
} // being called implicitly, so the compiler generates an error.
Example 2a: Class Complex defines a complex number, but the output operator has not
been defined for the class. Thus, when the user attempts to print out a
complex number, an error is not generated. Instead, the number is silently
converted to a real number by the conversion operator. This yields a
potentially surprising result to the client.
class Complex
{
public:
Complex (double r, double i = 1) : real(r), imaginary(i) {} // Constructor
operator double() const; // Conversion operator
… // converts Complex to double
private:
double real;
double imaginary;
};
Complex r(1,2);
cout << r << endl; // User might expect compile error, but instead
// r is automatically converted to decimal form
// potentially losing information.

Example 2b: Instead of the conversion operator, class Complex now has a member function
that performs the same role. Hence, the same functionality is maintained but without any
potential surprises.
class Complex
{
public:
Complex (double r, double i = 1) : real(r), imaginary(i) {} // Constructor
double as_double() const; // Conversion operator
… // converts Complex to double
private:
double real;
double imaginary;
};
Complex r(1,2);
cout << r << endl; // Compile error generated.
cout << r.asDouble() << endl; // Called explicitly rather than
// implicitly.
AV Rule 180
The following examples illustrate implicit conversions that result in the loss of information:
int32 i =1024;
char c = i; // Bad: (integer-to-char) implicit loss of information.
float32 f = 7.3;
int32 j= f; // Bad: (float-to-int) implicit loss of information.
int32 k = 1234567890;
float32 g = k; // Bad: (int-to-float) implicit loss of information
// (g will be 1234567936)
Note that an explicit cast to a narrower type (where the loss of information could occur) may
be used only where specifically required algorithmically. The explicit cast draws attention to
the fact that information loss is possible and that appropriate mitigations must be in place.

AV Rule 185
Traditional C-style casts raise several concerns. First, they enable most any type to be
converted to most any other type without any indication of the reason for the conversion
Next, the C-style cast syntax:
(type) expression // convert expression to be of type type.
is difficult to identify for both reviewers and tools. Consequently, both the location of
conversion expressions as well as the subsequent analysis of the conversion rationale proves
difficult for C-style casts.
Thus, C++ introduces several new-style casts (const_cast, dynamic_cast4, reinterpret_cast,
and static_cast) that address these problems. The new-style casts have the following form:
const_cast<type> (expression) // convert expression to be of type type.
reinterpret_cast<type> (expression)
static_cast<type> (expression)
Not only are these casts easy to identify, but they also communicate more precisely the
developer’s intent for applying a cast.
See also rule AV Rule 178 concerning conversions between derived classes and base classes.
AV Rule 187
ISO/IEC 14882 defines a side effect as a change in the state of the execution environment.
More precisely,
Accessing an object designated by a volatile lvalue, modifying an object, calling a library
I/O function, or calling a function that does any of those operations are all side effects,
which are changes in the state of the execution environment.
Example: Potential side effect
if (flag) // Has side effect only if flag is true.
{
foo();
}
Example: The following expression has no side effects
• 3 + 4; // Bad: statement has zero side effects
Example: The following expressions have side effects
• x = 3 + 4; // Statement has one side effect: x is set to 7.
• y = x++; // Statement two side effects: y is set to x and x is incremented.
4 Note that dynamic casts are not allowed at this point due to lack of tool support, but could be considered at some
point in the future after appropriate investigation has been performed for SEAL1/2 software.

AV Rule 192
Providing a final else clause (or comment indicating why a final else clause is unnecessary)
ensures all cases are handled in an else if series as illustrated by the following examples.
Example A: Final else clause not needed since there is no else if.
if (a < b)
{
foo();
}
Example B: Final else clause needed in case none of the prior conditions are satisfied.
if (a < b)
{
…
}
else if (b < c)
{
…
}
else if (c < d)
{
}
else // Final else clause needed
{
handle_error();
}
Example C: Final else clause not needed, since all possible conditions are handled.
Therefore a comment is included to clarify this condition.
if (status == error1)
{
handle_error1();
}
else if (status == error2)
{
handle_error2()
}
else if (status == error3)
{
handle_error3()
} // No final else needed: all possible errors are accounted for.

AV Rule 193
Terminating a non-empty case clause in a switch statement with a break statement eliminates
potentially confusing behavior by prohibiting control from falling through to subsequent
statements. In the example below, primary and secondary colors are handled similarly so
break statements are unneeded within each group. However, every non-empty case clause
must be terminated with a break statement for this segment of code to work as intended.
Note: Omitting the final default clause allows the compiler to provide a warning if all
enumeration values are not tested in the switch statement.
switch (value)
{
case red : // empty since primary_color() should be called
case green : // empty since primary_color() should be called
case blue : primary_color (value);
break; // Must break to end primary color handling
case cyan :
case magenta :
case yellow : secondary_color (value);
break; // Must break to end secondary color handling
case black : black (value);
break;
case white : white (value);
break;
}

AV Rule 204
AV Rule 204 attempts to prohibit side-effects in expressions that would be unclear,
misleading, obscure, or would otherwise result in unspecified or undefined behavior.
Consequently, an operation with side-effects will only be used in the following contexts:
Note: It is permissible for a side-effect to occur in conjunction with a constant expression.
However, care should be taken so that additional side-effects are not “hidden” within
the expression.
Note: Functions f(), g(), and h() have side-effects.
1. by itself
++i; // Good
for (int32 i=0 ; i<max ; ++i) // Good: includes the expression portion of a
// for statement
i++ - ++j; // Bad: operation with side-effect doesn’t occur by itself.
2. the right-hand side of an assignment
y = f(x); // Good
y = ++x; // Good: logically the same as y=f(x)
y = (-b + sqrt(b*b -4*a*c))/(2*a); // Good: sqrt() does not have side-effect
y = f(x) + 1; // Good: side-effect may occur with a constant
y = g(x) + h(z); // Bad: operation with side-effect doesn’t occur by itself
// on rhs of assignment
k = i++ - ++j; // Bad: same as above
y = f(x) + z; // Bad: same as above
3. a condition
if (x.f(y)) // Good
if (int x = f(y)) // Good: this form is often employed with dynamic casts
// if (D* pd = dynamic_cast<D*> (pb)) {…}
if (++p == NULL) /// Good: side-effect may occur with a constant
if (i++ - --j) // Bad: operation with side-effect doesn’t occur by itself
// in a condition
4. the only argument expression with a side-effect in a function call
f(g(z)); // Good
f(g(z),h(w)); // Bad: two argument expressions with side-effects
f(++i,++j); // Bad: same as above
f(g(z), 3); // Good: side-effect may occur with a constant

5. condition of a loop
while (f(x)) // Good
while(--x) // Good
while((c=*p++) != -1) // Bad: operation with side-effect doesn’t occur by itself
// in a loop condition
6. switch condition
switch (f(x)) // Good
switch (c = *p++) // Bad: operation with side-effect doesn’t occur by itself
// in a switch condition
7. single part of a chained operation
x.f().g().h(); // Good
a + b * c; // Good: (operator+() and operator*() are overloaded)
cout << x << y; // Good

AV Rule 204.1
Since the order in which operators and subexpression are evaluated is unspecified,
expressions must be written in a manner that produces the same value under any order the
standard permits.
i = v[i++]; // Bad: unspecified behavior
i = ++i + 1; // Bad: unspecified behavior
p->mem_func(*p++); // Bad: unspecified behavior
AV Rule 207
Unencapsulated global data can be dangerous and thus should be avoided. Note that objects
with only get and set methods, or get and set methods for each attribute are not considered to
be encapsulated.
int32 x=0; // Bad: Unencapsulated global object.
class Y {
in32 x;
public:
Y(int32 y_);
int32 get_x();
void set_x();
};
Y y (0); // Bad: Unencapsulated global object.
AV Rule 209
A UniversalTypes file will be created to define all standard types for developers to use. The
types include:
bool, // built-in type
char, // built-in type
int8, int16, int32, int64, // user-defined types
uint8, uint16, uint32, uint64, // user-defined types
float32, float64 // user-defined types
Note: Whether char represents signed or unsigned values is implementation-defined.
However, since modern implementations almost exclusively treat char as unsigned
char, the built-in char type will be used under the assumption that it is unsigned.

AV Rule 210.1
This rule is intended to prohibit an application from making assumptions concerning the
order in which non-static data members, separated by an access specifier, are ordered.
Consider Example A below. Class A can not be reliably “overlayed” on incoming message
data, since attribute ordering (across access specifiers) is unspecified.
In contrast, structure B may be reliably “overlayed” on the same incoming message data.
Example A:
class A
{
…
protected: // a could be stored before b, or vice versa
int32 a;
private:
int32 b;
};
…
// Bad: application assumes that objects of
// type A will always have attribute a
// stored before attribute b.
A* a_ptr = static_cast<A*>(message_buffer_ptr);
Example B:
struct B
{
int32 a;
int32 b;
};
…
// Good: attributes in B not separated
// by an access specifier
B* b_ptr = static_cast<B*>(message_buffer_ptr);

AV Rule 213
Parentheses should be used to clarify operator precedence rules to enhance readability and
reduce mistakes. However, overuse of parentheses can clutter an expression thereby reducing
readability. Requiring parenthesis below arithmetic operators strikes a reasonable balance
between readability and clutter.
Table 2 documents C++ operator precedence rules where items higher in the table have
precedence over those lower in the table.
Examples: Consider the following examples. Note that parentheses are required to specify
operator ordering for those operators below the arithmetic operators.
x = a * b + c; // Good: can assume “*” binds before “+”
x = v->a + v->b + w.c; // Good: can assume “->” and “.” Bind before “+”
x = (f()) + ((g()) * (h())); // Bad: overuse of parentheses. Can assume
// function call binds before “+” and “*”
x = a & b | c; // Bad: must use parenthesis to clarify order
x = a >> 1 + b; // Bad: must use parenthesis to clarify order

Table 2 Operator Precedence [2]
Operator Description Associativity
scope resolution class_name :: member left-to-right
scope resolution namespace_name :: member left-to-right
global :: name right-to-left
global :: qualified-name right-to-left
member selection object . member left-to-right
member selection pointer -> member
subscripting pointer [ expr ]
function call expr ( expr_list )
value construction type ( expr_list )
post increment lvalue ++
post decrement lvalue –
type identification typeid ( type )
run-time type identification typeid ( expr )
run-time checked conversion dynamic_cast < type > (expr )
compile-time checked conversion static_cast < type > (expr )
unchecked conversion reinterpret_cast < type > ( expr )
const conversion const_cast < type > ( expr )
size of object sizeof expr right-to-left
size of type sizeof ( type )
pre increment ++ lvalue
pre decrement -- lvalue
complement ~ expr
not ! expr
unary minus - expr
unary plus + expr
address of & lvalue
dereference * expr
create (allocate) new type
create (allocate and initialize) new type ( expr-list )
create (place) new (expr-list ) type
create (place and initialize) new (expr-list ) type ( expr-list )
destroy (deallocate) delete pointer
destroy array delete [] pointer
cast (type conversion) ( type ) expr
member selection object .* pointer-to-member left-to-right
member selection pointer ->* pointer-to-member
multiply expr * expr left-to-right
divide expr / expr
modulo (remainder) expr % expr
add (plus) expr + expr left-to-right
subtract (minus) expr – expr
shift left expr << expr left-to-right

shift right expr >> expr
less than expr < expr left-to-right
less than or equal expr <= expr
greater than expr > expr
greater than or equal expr >= expr
equal expr == expr left-to-right
not equal expr != expr
bitwise AND expr & expr left-to-right
bitwise exclusive OR expr ^ expr left-to-right
bitwise inclusive OR expr | expr left-to-right
logical AND expr && expr left-to-right
logical OR expr || expr left-to-right
conditional expression expr ? expr : expr right-to-left
simple assignment lvalue = expr right-to-left
multiply and assign lvalue *= expr
divide and assign lvalue /= expr
modula and assign lvalue %= expr
add and assign lvalue += expr
subtract and assign lvalue -= expr
shift left and assign lvalue <<= expr
shift right and assign lvalue >>= expr
AND and assign lvalue &= expr
inclusive OR and assign lvalue |= expr
exclusive OR and assign lvalue ^= expr
throw exception throw expr right-to-left
comma (sequencing) expr , expr left-to-right

AV Rule 214
The order of initialization for non-local static objects may present problems. For example, a
non-local static object may not be used in a constructor if that object will not be initialized
before the constructor runs. At present, the order of initialization for non-local static objects,
which are defined in different compilation units, is not defined. This can lead to errors that
are difficult to locate.
The problem may be resolved by moving each non-local static object to its own function
where it becomes a local static object. If the function returns a reference to the local static
object it contains, then clients may access the object via the function without any of the
initialization order problems. Note that the function can be inlined to eliminate the function
call overhead.
Example:
// file 1
static int32 x = 5;
// file 2
static int32 y = x + 1; // Bad assumption. The compiler might not have initialized
// static variable x.
The solution is to substitute static local objects for static non-local objects since the creation
time is precisely defined for static local objects: the first time through the enclosing function.
inline Resource& the_resource()
{
static Resource r;
return r;
}
Now clients may at any time reference the Resource object, r, as the_resource() without
consideration for the order of initialization among r and any other similarly defined local
static objects.
Alternately, one might consider allocating objects in a memory pool or on a stack at startup.
AV Rule 215
Pointers should be eliminated from user interfaces wherever possible. Instead, objects with
well defined interfaces should be used to hide pointers from clients as well as to ensure any
pointer manipulation would be performed in a well-defined manner. For example, passing an
Array object (instead of a raw array) through an interface eliminates the array decay problem
and hence any pointer arithmetic required on the receiving end.
AV Rule 216
The overall performance of a program is usually determined by a relatively small portion of
code. This is often referred to as the “80-20 Rule” which states that 80% of the time is spent
in only 20% of the code. Thus, design and coding decisions should be made from a safety
and clarity perspective with efficiency as a secondary goal. Only after adequate profiling
analysis has been performed (where the true bottlenecks have been identified) should
attempts at optimization be made.

AV Rule 220
Consider the class diagram in Example A where method_1() is inherited by classes B and C.
Suppose portions of method_1() (indicated by the shaded regions) are executed in each of A,
B, and C such that 100% of method_1() is covered, but not in any one context. A report
generated at the method level would produce a misleading view of coverage.
Alternately, consider the flattened class diagram in Example B. Each method is considered in
the context of the flattened class in which it exists. Hence coverage of method_1() is reported
independently for each context (A, B, and C).
Example A: Structural coverage of concrete (non-inherited) attributes produces a single
report purporting 100% coverage of method_1(). However, method_1() was not completely
covered in any one context.
A
Structural
Coverage in A
Coverage
method_1
Report
Coverage in B
(100%)
Coverage in C
B C
method_2 method_3

Example B: Structural coverage of the flattened hierarchy considers method_1() to be a
member of each derived class. Hence an individual coverage report is generated for
method_1() in the context of classes A, B, and C.
A
Structural
Coverage in A
Coverage
method_1
Report
Coverage in B
Coverage in C
B C
method_1 method_1
method 2 method 3

APPENDIX B (COMPLIANCE)
“LDRA_Compliance” lists the rules in this document that can be automatically checked by
LDRA. Rules not checked by LDRA will be verified by manual inspection and results captured
on checklists.
Note that if other tools are employed to automatically check rules not checked by LDRA, this
appendix should be updated to reflect the source of verification
