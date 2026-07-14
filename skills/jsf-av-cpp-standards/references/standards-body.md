JOINT STRIKE FIGHTER
AIR VEHICLE
C++ CODING STANDARDS
FOR THE SYSTEM DEVELOPMENT AND DEMONSTRATION PROGRAM
Document Number 2RDU00001 Rev C
December 2005
Copyright 2005 by Lockheed Martin Corporation.
DISTRIBUTION STATEMENT A: Approved for public release; distribution is unlimited.

This page intentionally left blank

TABLE OF CONTENTS
1 Introduction.............................................................................................................................7
2 Referenced Documents...........................................................................................................8
3 General Design......................................................................................................................10
3.1 Coupling & Cohesion...................................................................................................11
3.2 Code Size and Complexity............................................................................................12
4 C++ Coding Standards..........................................................................................................13
4.1 Introduction...................................................................................................................13
4.2 Rules.............................................................................................................................13
4.2.1 Should, Will, and Shall Rules...............................................................................13
4.2.2 Breaking Rules......................................................................................................13
4.2.3 Exceptions to Rules...............................................................................................14
4.3 Terminology..................................................................................................................14
4.4 Environment..................................................................................................................17
4.4.1 Language...............................................................................................................17
4.4.2 Character Sets.......................................................................................................17
4.4.3 Run-Time Checks.................................................................................................18
4.5 Libraries........................................................................................................................19
4.5.1 Standard Libraries.................................................................................................19
4.6 Pre-Processing Directives.............................................................................................20
4.6.1 #ifndef and #endif Pre-Processing Directives......................................................20
4.6.2 #define Pre-Processing Directive..........................................................................21
4.6.3 #include Pre-Processing Directive........................................................................21
4.7 Header Files..................................................................................................................22
4.8 Implementation Files....................................................................................................23
4.9 Style..............................................................................................................................23
4.9.1 Naming Identifiers................................................................................................24
4.9.1.1 Naming Classes, Structures, Enumerated types and typedefs..........................25
4.9.1.2 Naming Functions, Variables and Parameters..................................................26
4.9.1.3 Naming Constants and Enumerators.................................................................26
4.9.2 Naming Files.........................................................................................................26
4.9.3 Classes...................................................................................................................27
4.9.4 Functions...............................................................................................................27
4.9.5 Blocks...................................................................................................................28
4.9.6 Pointers and References........................................................................................28
4.9.7 Miscellaneous.......................................................................................................28
4.10 Classes...........................................................................................................................29
4.10.1 Class Interfaces.....................................................................................................29
4.10.2 Considerations Regarding Access Rights.............................................................29
4.10.3 Member Functions................................................................................................29
4.10.4 const Member Functions.......................................................................................30
4.10.5 Friends...................................................................................................................30
4.10.6 Object Lifetime, Constructors, and Destructors...................................................30
4.10.6.1 Object Lifetime.............................................................................................30
4.10.6.2 Constructors..................................................................................................31
4.10.6.3 Destructors....................................................................................................32
4.10.7 Assignment Operators...........................................................................................33

4.10.8 Operator Overloading...........................................................................................33
4.10.9 Inheritance.............................................................................................................34
4.10.10 Virtual Member Functions................................................................................37
4.11 Namespaces...................................................................................................................38
4.12 Templates......................................................................................................................39
4.13 Functions.......................................................................................................................40
4.13.1 Function Declaration, Definition and Arguments.................................................40
4.13.2 Return Types and Values......................................................................................41
4.13.3 Function Parameters (Value, Pointer or Reference).............................................42
4.13.4 Function Invocation..............................................................................................42
4.13.5 Function Overloading...........................................................................................43
4.13.6 Inline Functions....................................................................................................43
4.13.7 Temporary Objects................................................................................................44
4.14 Comments.....................................................................................................................44
4.15 Declarations and Definitions.........................................................................................46
4.16 Initialization..................................................................................................................47
4.17 Types.............................................................................................................................48
4.18 Constants.......................................................................................................................48
4.19 Variables.......................................................................................................................49
4.20 Unions and Bit Fields....................................................................................................50
4.21 Operators.......................................................................................................................51
4.22 Pointers & References...................................................................................................52
4.23 Type Conversions.........................................................................................................54
4.24 Flow Control Structures................................................................................................56
4.25 Expressions...................................................................................................................58
4.26 Memory Allocation.......................................................................................................59
4.27 Fault Handling..............................................................................................................59
4.28 Portable Code................................................................................................................60
4.28.1 Data Abstraction...................................................................................................60
4.28.2 Data Representation..............................................................................................60
4.28.3 Underflow/Overflow.............................................................................................61
4.28.4 Order of Execution................................................................................................61
4.28.5 Pointer Arithmetic.................................................................................................61
4.29 Efficiency Considerations.............................................................................................62
4.30 Miscellaneous...............................................................................................................62
5 Testing...................................................................................................................................63
5.1.1 Subtypes................................................................................................................63
5.1.2 Structure................................................................................................................63
Appendix A...................................................................................................................................66
Appendix B (Compliance)..........................................................................................................142

Table 1. Change Log
Revision Document Change Affected Comments
ID Date Authority Paragraphs
0001 Rev B Oct 2005 K. Carroll All Original
0001 Rev C Nov 2005 K. Carroll Change log - Added Add change log.
Section 1, point 3 Corrected spelling
Rule 52 errors.
Rule 76
Rule 91
Rule 93
Rule 129
Rule 167
Rule 218
Appendix A, Rule 3
Table 2
Rule 159 - clarify that Both binary and unary
"unary &" is intended. forms of "&" exist.
Clarification is added
to specify that the rule
is concerned with the
unary form.
Rule 32 - clarification of The rule does not
the scope of the rule. Also, apply to a particular
example added in appendix partitioning of
for rule 32. template classes and
functions.

1 INTRODUCTION
The intent of this document is to provide direction and guidance to C++ programmers that will
enable them to employ good programming style and proven programming practices leading to
safe, reliable, testable, and maintainable code. Consequently, the rules contained in this
document are required for Air Vehicle C++ development1 and recommended for non-Air
Vehicle C++ development.
As indicated above, portions of Air Vehicle (AV) code will be developed in C++. C++ was
designed to support data abstraction, object-oriented programming, and generic programming
while retaining compatibility with traditional C programming techniques. For this reason, the
AV Coding Standards will focus on the following:
1. Motor Industry Software Reliability Association (MISRA) Guidelines For The Use Of
The C Language In Vehicle Based Software,
2. Vehicle Systems Safety Critical Coding Standards for C, and
3. C++ language-specific guidelines and standards.
The MISRA Guidelines were written specifically for use in systems that contain a safety aspect
to them. The guidelines address potentially unsafe C language features, and provide
programming rules to avoid those pitfalls. The Vehicle Systems Safety Critical Coding Standards
for C, which are based on the MISRA C subset, provide a more comprehensive set of language
restrictions that are applied uniformly across Vehicle Systems safety critical applications. The
AV Coding Standards build on the relevant portions of the previous two documents with an
additional set of rules specific to the appropriate use C++ language features (e.g. inheritance,
templates, namespaces, etc.) in safety-critical environments.
Overall, the philosophy embodied by the rule set is essentially an extension of C++’s philosophy
with respect to C. That is, by providing “safer” alternatives to “unsafe” facilities, known
problems with low-level features are avoided. In essence, programs are written in a “safer”
subset of a superset.
1 TBD: Required for Air Vehicle non-prime teams?

2 REFERENCED DOCUMENTS
1. ANSI/IEEE Std 754, IEEE Standard for Binary Floating-Point Arithmetic, 1985.
2. Bjarne Stroustrup. The C++ Programming Language, 3rd Edition. Addison-Wesley,
2000.
3. Bjarne Stroustrup. Bjarne Stroustrup's C++ Glossary.
4. Bjarne Stroustrup. Bjarne Stroustrup's C++ Style and Technique FAQ.
5. Barbara Liskov. Data Abstraction and Hierarchy, SIGPLAN Notices, 23, 5 (May, 1988).
6. Scott Meyers. Effective C++: 50 Specific Ways to Improve Your Programs and Design,
2nd Edition. Addison-Wesley, 1998.
7. Scott Meyers. More Effective C++: 35 New Ways to Improve Your Programs and
Designs. Addison-Wesley, 1996.
8. Motor Industry Software Reliability Association. Guidelines for the Use of the C
Language in Vehicle Based Software, April 1998.
9. ISO/IEC 10646-1, Information technology - Universal Multiple-Octet Coded Character
Set (UCS) - Part 1: Architecture and Basic Multilingual Plane, 1993.
10. ISO/IEC 14882:2003(E), Programming Languages – C++. American National Standards
Institute, New York, New York 10036, 2003.
11. ISO/IEC 9899: 1990, Programming languages - C, ISO, 1990.
12. JSF Mission Systems Software Development Plan.
13. JSF System Safety Program Plan. DOC. No. 2YZA00045-0002.
14. Programming in C++ Rules and Recommendations.
Copyright © by Ellemtel Telecommunication Systems Laboratories
Box 1505, 125 25 Alvsjo, Sweden
Document: M 90 0118 Uen, Rev. C, 27 April 1992.
Used with permission supplied via the following statement:
Permission is granted to any individual or institution to use, copy, modify and distribute
this document, provided that this complete copyright and permission notice is maintained
intact in all copies.

15. RTCA/DO-178B, Software Considerations in Airborne Systems and Equipment
Certification, December 1992.

3 GENERAL DESIGN
This coding standards document is intended to help programmers develop code that conforms to
safety-critical software principles, i.e., code that does not contain defects that could lead to
catastrophic failures resulting in significant harm to individuals and/or equipment. In general, the
code produced should exhibit the following important qualities:
Reliability: Executable code should consistently fulfill all requirements in a predictable manner.
Portability: Source code should be portable (i.e. not compiler or linker dependent).
Maintainability: Source code should be written in a manner that is consistent, readable, simple
in design, and easy to debug.
Testability: Source code should be written to facilitate testability. Minimizing the following
characteristics for each software module will facilitate a more testable and maintainable module:
1. code size
2. complexity
3. static path count (number of paths through a piece of code)
Reusability: The design of reusable components is encouraged. Component reuse can eliminate
redundant development and test activities (i.e. reduce costs).
Extensibility: Requirements are expected to evolve over the life of a product. Thus, a system
should be developed in an extensible manner (i.e. perturbations in requirements may be managed
through local extensions rather than wholesale modifications).
Readability: Source code should be written in a manner that is easy to read, understand and
comprehend.
Note that following the guidelines contained within this document will not guarantee the
production of an error-free, safe product. However, adherence to these guidelines, as well as the
processes defined in the Software Development Plan [12], will help programmers produce clean
designs that minimize common sources of mistakes and errors.

3.1 Coupling & Cohesion
Coupling and cohesion are properties of a system that has been decomposed into modules.
Cohesion is a measure of how well the parts in the same module fit together. Coupling is a
measure of the amount of interaction between the different modules in a system. Thus, cohesion
deals with the elements within a module (how well-suited elements are to be part of the same
module) while coupling deals with the relationships among modules (how tightly modules are
glued together).
Object-oriented design and implementation generally support desirable coupling and cohesion
characteristics. The design principles behind OO techniques lead to data cohesion within
modules. Clean interfaces between modules enable the modules to be loosely coupled.
Moreover, data encapsulation and data protection mechanisms provide a means to help enforce
the coupling and cohesion goals.
Source code should be developed as a set of modules as loosely coupled as is reasonably
feasible. Note that generic programming (which requires the use of templates) allows source
code to be written with loose coupling and without runtime overhead.
Examples of tightly coupled software would include the following:
• many functions tied closely to hardware or other external software sources, and
• many functions accessing global data.
There may be times where tightly coupled software is unavoidable, but its use should be both
minimized and localized as suggested by the following guidelines:
• limit hardware and external software interfaces to a small number of functions,
• minimize the use of global data, and
• minimize the exposure of implementation details.

3.2 Code Size and Complexity
AV Rule 1
Any one function (or method) will contain no more than 200 logical source lines of code (L-
SLOCs).
Rationale: Long functions tend to be complex and therefore difficult to comprehend and test.
Note: Section 4.2.1 defines should and shall rules as well the conditions under which
deviations from should or shall rules are allowed.
AV Rule 2
There shall not be any self-modifying code.
Rationale: Self-modifying code is error-prone as well as difficult to read, test, and maintain.
AV Rule 3
All functions shall have a cyclomatic complexity number of 20 or less.
Rationale: Limit function complexity. See AV Rule 3 in Appendix A for additional details.
Exception: A function containing a switch statement with many case labels may exceed this
limit.
Note: Section 4.2.1 defines should and shall rules as well the conditions under which
deviations from should or shall rules are allowed.

4 C++ CODING STANDARDS
4.1 Introduction
The purpose of the following rules and recommendations is to define a C++ programming style
that will enable programmers to produce code that is more:
• correct,
• reliable, and
• maintainable.
In order to achieve these goals, programs should:
• have a consistent style,
• be portable to other architectures,
• be free of common types of errors, and
• be understandable, and hence maintainable, by different programmers.
4.2 Rules
4.2.1 Should, Will, and Shall Rules
There are three types of rules: should, will, and shall rules. Each rule contains either a
“should”, “will” or a “shall” in bold letters indicating its type.
• Should rules are advisory rules. They strongly suggest the recommended way of
doing things.
• Will rules are intended to be mandatory requirements. It is expected that they will be
followed, but they do not require verification. They are limited to non-safety-critical
requirements that cannot be easily verified (e.g., naming conventions).
• Shall rules are mandatory requirements. They must be followed and they require
verification (either automatic or manual).
4.2.2 Breaking Rules
AV Rule 4
To break a “should” rule, the following approval must be received by the developer:
• approval from the software engineering lead (obtained by the unit approval in the
developmental CM tool)
AV Rule 5
To break a “will” or a “shall” rule, the following approvals must be received by the
developer:
• approval from the software engineering lead (obtained by the unit approval in the
developmental CM tool)
• approval from the software product manager (obtained by the unit approval in the
developmental CM tool)

AV Rule 6
Each deviation from a “shall” rule shall be documented in the file that contains the
deviation). Deviations from this rule shall not be allowed, AV Rule 5 notwithstanding.
4.2.3 Exceptions to Rules
Some rules may contain exceptions. If a rule does contain an exception, then approval is not
required for a deviation allowed by that exception
AV Rule 7
Approval will not be required for a deviation from a “shall” or “will” rule that complies
with an exception specified by that rule.
4.3 Terminology
1. An abstract base class is a class from which no objects may be created; it is only used as
a base class for the derivation of other classes. A class is abstract if it includes at least one
member function that is declared as pure virtual.
2. An abstract data type is a type whose internal form is hidden behind a set of access
functions. Objects of the type are created and inspected only by calls to the access
functions. This allows the implementation of the type to be changed without requiring
any changes outside the module in which it is defined.
3. An accessor function is a function which returns the value of a data member.
4. A catch clause is code that is executed when an exception of a given type is raised. The
definition of an exception handler begins with the keyword catch.
5. A class is a user-defined data type which consists of data elements and functions which
operate on that data. In C++, this may be declared as a class; it may also be declared as a
struct or a union. Data defined in a class is called member data and functions defined in a
class are called member functions.
6. A class template defines a family of classes. A new class may be created from a class
template by providing values for a number of arguments. These values may be names of
types or constant expressions.
7. A compilation unit is the source code (after preprocessing) that is submitted to a
compiler for compilation (including syntax checking).
8. A concrete type is a type without virtual functions, so that objects of the type can be
allocated on the stack and manipulated directly (without a need to use pointers or
references to allow the possibility for derived classes). Often, small self-contained
classes. [3]
9. A constant member function is a function which may not modify data members.
10. A constructor is a function which initializes an object.

11. A copy constructor is a constructor in which the first argument is a reference to an
object that has the same type as the object to be initialized.
12. Dead code is “executable object code (or data) which, as a result of a design error cannot
be executed (code) or used (data) in an operational configuration of the target computer
environment and is not traceable to a system or software requirement.” [9]
13. A declaration of a variable or function announces the properties of the variable or
function; it consists of a type name and then the variable or function name. For
functions, it tells the compiler the name, return type and parameters. For variables, it
tells the compiler the name and type.
int32 fahr;
int32 foo ();
14. A default constructor is a constructor which needs no arguments.
15. A definition of a function tells the compiler how the function works. It shows what
instructions are executed for the function.
int32 foo ()
{
// Statements
}
16. An enumeration type is an explicitly declared set of symbolic integer constants. In C++
it is declared as an enum.
17. An exception is a run-time program anomaly that is detected in a function or member
function. Exception handling provides for the uniform management of exceptions.
18. A forwarding function is a function which does nothing more than call another function.
19. A function template defines a family of functions. A new function may be created from
a function template by providing values for a number of arguments. These values may be
names of types or constant expressions.
20. An identifier is a name which is used to refer to a variable, constant, function or type in
C++. When necessary, an identifier may have an internal structure which consists of a
prefix, a name, and a suffix (in that order).
21. An iterator is an object that con be used to traverse a data structure.
22. A macro is a name for a text string which is defined in a #define statement. When this
name appears in source code, the compiler replaces it with the defined text string.
23. Multiple inheritance is the derivation of a new class from more than one base class.

24. A mutator function is a function which sets the value of a data member.
25. The one definition rule - there must be exactly one definition of each entity in a
program. If more than one definition appears, say because of replication through header
files, the meaning of all such duplicates must be identical. [3]
26. An overloaded function name is a name which is used for two or more functions or
member functions having different argument types.
27. An overridden member function is a member function in a base class which is re-
defined in a derived class.
28. A built-in data type is a type which is defined in the language itself, such as int.
29. Protected members of a class are member data and member functions which are
accessible by specifying the name within member functions of derived classes.
30. Public members of a class are member data and member functions which are accessible
everywhere by specifying an instance of the class and the name.
31. A pure virtual function is one with an initializer = 0 in its declaration. Making a virtual
function pure makes the class abstract. A pure virtual function must be overridden in at
least one derived class.
32. A reference is another name for a given variable. In C++, the ‘address of’ (&) operator is
used immediately after the data type to indicate that the declared variable, constant, or
function argument is a reference.
33. The scope of a name refers to the context in which it is visible. [Context, here, means the
functions or blocks in which a given variable name can be used.]
34. A side effect is the change of a variable as a by-product of an evaluation of an
expression.
35. A structure is a user-defined type for which all members are public by default.
36. A typedef is another name for a data type, specified in C++ using a typedef declaration.
37. Unqualified type is a type that does not have const or volatile as a qualifier.
38. A user-defined data type is a type which is defined by a programmer in a class, struct,
union, or enum definition or as an instantiation of a class template.

4.4 Environment
4.4.1 Language
AV Rule 8
All code shall conform to ISO/IEC 14882:2002(E) standard C++. [10]
Rationale: ISO/IEC 14882 is the international standard that defines the C++ programming
language. Thus all code shall be well-defined with respect to ISO/IEC 14882. Any language
extensions or variations from ISO/IEC 14882 shall not be allowed.
4.4.2 Character Sets
Note that the rules in this section may need to be modified if one or more foreign languages will
be used for input/output purposes (e.g. displaying information to pilots).
AV Rule 9 (MISRA Rule 5, Revised)
Only those characters specified in the C++ basic source character set will be used. This set
includes 96 characters: the space character, the control characters representing horizontal tab,
vertical tab, form feed, and newline, and the following 91 graphical characters:
a b c d e f g h i j k l m n o p q r s t u v w x y z
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
0 1 2 3 4 5 6 7 8 9
_ { } [ ] # ( ) < > % : ; . ? * + -
/ ^ & | ~ ! = , \ " ’
Rationale: Minimal required character set.
AV Rule 10 (MISRA Rule 6)
Values of character types will be restricted to a defined and documented subset of ISO
10646-1. [9]
Rationale: 10646-1 represents an international standard for character mapping. For the basic
source character set, the 10646-1 mapping corresponds to the ASCII mapping.
AV Rule 11 (MISRA Rule 7)
Trigraphs will not be used.
Trigraph sequences are three-character sequences that are replaced by a corresponding single
character, as follows:
Alternative Primary alternative primary alternative primary
??= # ??( [ ??< {
??/ \ ??) ] ??> }
??' ^ ??! | ??- ~
The trigraph sequences provide a way to specify characters that are missing on some
terminals, but that the C++ language uses.

Rationale: Readability. See AV Rule 11 in Appendix A.
Note: trigraphs can often be disabled via compiler flags (e.g.–no_alternative_tokens for
the Green Hills C/C++ compiler suite)
AV Rule 12 (Extension of MISRA Rule 7)
The following digraphs will not be used:
Alternative Primary alternative Primary
<% { :> ]
%> } %: #
<: [ %:%: ##
The digraphs listed above provide a way to specify characters that are missing on some
terminals, but that the C++ language uses.
Rationale: Readability. See AV Rule 12 in Appendix A.
Note: Digraphs can often be disabled via compiler flags (e.g.–no_alternative_tokens for
the Green Hills C/C++ compiler suite)
AV Rule 13 (MISRA Rule 8)
Multi-byte characters and wide string literals will not be used.
Rationale: Both multi-byte and wide characters may be composed of more than one byte.
However, certain aspects of the behavior of multi-byte characters are implementation-
defined. [10]
AV Rule 14
Literal suffixes shall use uppercase rather than lowercase letters.
Rationale: Readability.
Example:
const int64 fs_frame_rate = 64l; // Wrong! Looks too much like 641
const int64 fs_frame_rate = 64L; // Okay
4.4.3 Run-Time Checks
AV Rule 15 (MISRA Rule 4, Revised)
Provision shall be made for run-time checking (defensive programming).
Rationale: For SEAL 1 or SEAL 2 software [13], provisions shall be made to ensure the
proper operation of software and system function. See AV Rule 15 in Appendix A for
additional details.

4.5 Libraries
AV Rule 16
Only DO-178B level A [15] certifiable or SEAL 1 C/C++ libraries shall be used with safety-
critical (i.e. SEAL 1) code [13].
Rationale: Safety.
Note: All libraries used must be DO-178B level A certifiable or written in house and
developed using the same software development processes required for all other
safety-critical software. This includes both the run-time library functions as well as
the C/C++ standard library functions. [10,11] Note that we expect certifiable versions
of the C++ standard libraries to be available at some point in the future. These
certifiable libraries would be allowed under this rule.
4.5.1 Standard Libraries
AV Rule 17 through AV Rule 25 prohibit the use of a number of features whose behaviors are
local-specific, unspecified, undefined, implementation-defined, or otherwise poorly defined and
hence error prone.
AV Rule 17 (MISRA Rule 119)
The error indicator errno shall not be used.
Exception: If there is no other reasonable way to communicate an error condition to an
application, then errno may be used. For example, third party math libraries will often make
use of errno to inform an application of underflow/overflow or out-of-range/domain
conditions. Even in this case, errno should only be used if its design and implementation are
well-defined and documented.
AV Rule 18 (MISRA Rule 120)
The macro offsetof, in library <stddef.h>, shall not be used.
AV Rule 19 (MISRA Rule 121)
<locale.h> and the setlocale function shall not be used.
AV Rule 20 (MISRA Rule 122)
The setjmp macro and the longjmp function shall not be used.
AV Rule 21 (MISRA Rule 123)
The signal handling facilities of <signal.h> shall not be used.
AV Rule 22 (MISRA Rule 124, Revised)
The input/output library <stdio.h> shall not be used.
AV Rule 23 (MISRA Rule 125)
The library functions atof, atoi and atol from library <stdlib.h> shall not be used.

Exception: If required, atof, atoi and atol may be used only after design and implementation
are well-defined and documented, especially in regards to precision and failures in string
conversion attempts.
AV Rule 24 (MISRA Rule 126)
The library functions abort, exit, getenv and system from library <stdlib.h> shall not be used.
AV Rule 25 (MISRA Rule 127)
The time handling functions of library <time.h> shall not be used.
4.6 Pre-Processing Directives
Since the pre-processor knows nothing about C++, it should not be used to do what can
otherwise be done in C++.
AV Rule 26
Only the following pre-processor directives shall be used:
1. #ifndef
2. #define
3. #endif
4. #include
Rationale: Limit the use of the pre-processor to those cases where it is necessary.
Note: Allowable uses of these directives are specified in the following rules.
4.6.1 #ifndef and #endif Pre-Processing Directives
AV Rule 27
#ifndef, #define and #endif will be used to prevent multiple inclusions of the same header
file. Other techniques to prevent the multiple inclusions of header files will not be used.
Rationale: Eliminate multiple inclusions of the same header file in a standard way.
Example: For SomeHeaderFileName.h
#ifndef Header_filename
#define Header_filename
// Header declarations…
#endif
AV Rule 28
The #ifndef and #endif pre-processor directives will only be used as defined in AV Rule 27
to prevent multiple inclusions of the same header file.
Rationale: Conditional code compilation should be kept to a minimum as it can significantly
obscure testing and maintenance efforts.

4.6.2 #define Pre-Processing Directive
AV Rule 29
The #define pre-processor directive shall not be used to create inline macros. Inline functions
shall be used instead.
Rationale: Inline functions do not require text substitutions and behave well when called
with arguments (e.g. type checking is performed). See AV Rule 29 in Appendix A for an
example.
See section 4.13.6 for rules pertaining to inline functions.
AV Rule 30
The #define pre-processor directive shall not be used to define constant values. Instead, the
const qualifier shall be applied to variable declarations to specify constant values.
Exception: The only exception to this rule is for constants that are commonly defined by
third-party modules. For example, #define is typically used to define NULL in standard
header files. Consequently, NULL may be treated as a macro for compatibility with third-
party tools.
Rationale: const variables follow scope rules, are subject to type checking and do not require
text substitutions (which can be confusing or misleading). See AV Rule 30 in Appendix A
for an example.
AV Rule 31
The #define pre-processor directive will only be used as part of the technique to prevent
multiple inclusions of the same header file.
Rationale: #define can be used to specify conditional compilation (AV Rule 27 and AV Rule
28), inline macros (AV Rule 29) and constants (AV Rule 30). This rule specifies that the only
allowable use of #define is to prevent multiple includes of the same header file (AV Rule 27).
4.6.3 #include Pre-Processing Directive
AV Rule 32
The #include pre-processor directive will only be used to include header (*.h) files.
Exception: In the case of template class or function definitions, the code may be partitioned
into separate header and implementation files. In this case, the implementation file may be
included as a part of the header file. The implementation file is logically a part of the header
and is not separately compilable. See AV Rule 32 in Appendix A.
Rationale: Clarity. The only files included in a .cpp file should be the relevant header (*.h)
files.

4.7 Header Files
AV Rule 33
The #include directive shall use the <filename.h> notation to include header files.
Note that relative pathnames may also be used. See also AV Rule 53, AV Rule 53.1, and AV
Rule 55 for additional information regarding header file names.
Rationale: The include form “filename.h” is typically used to include local header files.
However, due to the unfortunate divergence in vendor implementations, only the
<filename.h> form will be used.
Examples:
#include <foo.h> // Good
#include <dir1/dir2/foo.h> // Good: relative path used
#include “foo.h” // Bad: “filename.h” form used
AV Rule 34
Header files should contain logically related declarations only.
Rationale: Minimize unnecessary dependencies.
AV Rule 35
A header file will contain a mechanism that prevents multiple inclusions of itself.
Rationale: Avoid accidental header file recursion. Note AV Rule 27 specifies the
mechanism by which multiple inclusions are to be eliminated whereas this rule (AV Rule 35)
specifies that each header file must use that mechanism.
AV Rule 36
Compilation dependencies should be minimized when possible. (Stroustrup [2], Meyers [6],
item 34)
Rationale: Minimize unnecessary recompilation of source files. See AV Rule 36 in
Appendix A for an example.
Note: AV Rule 37 and AV Rule 38 detail several mechanisms by which compilation
dependencies may be minimized.
AV Rule 37
Header (include) files should include only those header files that are required for them to
successfully compile. Files that are only used by the associated .cpp file should be placed in
the .cpp file—not the .h file.
Rationale: The #include statements in a header file define the dependencies of the file.
Fewer dependencies imply looser couplings and hence a smaller ripple-effect when the
header file is required to change.

AV Rule 38
Declarations of classes that are only accessed via pointers (*) or references (&) should be
supplied by forward headers that contain only forward declarations.
Rationale: The header files of classes that are only referenced via pointers or references need
not be included. Doing so often increases the coupling between classes, leading to increased
compilation dependencies as well as greater maintenance efforts. Forward declarations of
the classes in question (supplied by forward headers) can be used to limit implementation
dependencies, maintenance efforts and compile times. See AV Rule 38 in Appendix A for an
example. Note that this technique is employed in the standard header <iosfwd> to declare
forward references to template classes used throughout <iostreams>.
AV Rule 39
Header files (*.h) will not contain non-const variable definitions or function definitions. (See
also AV Rule 139.)
Rationale: Header files should typically contain interface declarations—not implementation
details.
Exception: Inline functions and template definitions may be included in header files. See AV
Rule 39 in Appendix A for an example.
4.8 Implementation Files
AV Rule 40
Every implementation file shall include the header files that uniquely define the inline
functions, types, and templates used.
Rationale: Insures consistency checks. (See AV Rule 40 Appendix in A for additional
details)
Note that this rule implies that the definition of a particular inline function, type, or template
will never occur in multiple header files.
4.9 Style
Imposing constraints on the format of syntactic elements makes source code easier to read due to
consistency in form and appearance. Note that automatic code generators should be configured to
produce code that conforms to the style guidelines where possible. However, an exception is
made for code generators that cannot be reasonably configured to comply with should or will
style rules (safety-critical shall rules must still be followed).
AV Rule 41
Source lines will be kept to a length of 120 characters or less.
Rationale: Readability and style. Very long source lines can be difficult to read and
understand.

AV Rule 42
Each expression-statement will be on a separate line.
Rationale: Simplicity, readability, and style. See AV Rule 42 in Appendix A for examples.
AV Rule 43
Tabs should be avoided.
Rationale: Tabs are interpreted differently across various editors and printers.
Note: many editors can be configured to map the ‘tab’ key to a specified number of spaces.
AV Rule 44
All indentations will be at least two spaces and be consistent within the same source file.
Rationale: Readability and style.
4.9.1 Naming Identifiers
The choice of identifier names should:
• Suggest the usage of the identifier.
• Consist of a descriptive name that is short yet meaningful.
• Be long enough to avoid name conflicts, but not excessive in length.
• Include abbreviations that are generally accepted.
Note: In general, the above guidelines should be followed. However, conventional usage of
simple identifiers (i, x, y, p, etc.) in small scopes can lead to cleaner code and will
therefore be permitted.
Additionally, the term ‘word’ in the following naming convention rules may be used to refer
to a word, an acronym, an abbreviation, or a number.
AV Rule 45
All words in an identifier will be separated by the ‘_’ character.
Rationale: Readability and Style.
AV Rule 46 (MISRA Rule 11, Revised)
User-specified identifiers (internal and external) will not rely on significance of more than 64
characters.
Note: The C++ standard suggests that a minimum of 1,024 characters will be significant.
[10]
AV Rule 47
Identifiers will not begin with the underscore character ‘_’.
Rationale: ‘_’ is often used as the first character in the name of library functions (e.g. _main,
_exit, etc.) In order to avoid name collisions, identifiers should not begin with ‘_’.

AV Rule 48
Identifiers will not differ by:
• Only a mixture of case
• The presence/absence of the underscore character
• The interchange of the letter ‘O’, with the number ‘0’ or the letter ‘D’
• The interchange of the letter ‘I’, with the number ‘1’ or the letter ‘l’
• The interchange of the letter ‘S’ with the number ‘5’
• The interchange of the letter ‘Z’ with the number 2
• The interchange of the letter ‘n’ with the letter ‘h’.
Rationale: Readability.
AV Rule 49
All acronyms in an identifier will be composed of uppercase letters.
Note: An acronym will always be in upper case, even if the acronym is located in a portion
of an identifier that is specified to be lower case by other rules.
Rationale: Readability.
4.9.1.1 Naming Classes, Structures, Enumerated types and typedefs
AV Rule 50
The first word of the name of a class, structure, namespace, enumeration, or type created
with typedef will begin with an uppercase letter. All others letters will be lowercase.
Rationale: Style.
Example:
class Diagonal_matrix { … }; // Only first letter is capitalized;
enum RGB_colors {red, green, blue}; // RGB is an acronym so all letters are un upper case
Exception: The first letter of a typedef name may be in lowercase in order to conform to a
standard library interface or when used as a replacement for fundamental types (see AV Rule
209).
typename C::value_type s=0; // value_type of container C begins with a lower case
//letter in conformance with standard library typedefs

4.9.1.2 Naming Functions, Variables and Parameters
AV Rule 51
All letters contained in function and variable names will be composed entirely of lowercase
letters.
Rationale: Style.
Example:
class Example_class_name
{
public:
uint16 example_function_name (void);
private:
uint16 example_variable_name;
};
4.9.1.3 Naming Constants and Enumerators
AV Rule 52
Identifiers for constant and enumerator values shall be lowercase.
Example:
const uint16 max_pressure = 100;
enum Switch_position {up, down};
Rationale: Although it is an accepted convention to use uppercase letters for constants and
enumerators, it is possible for third party libraries to replace constant/enumerator names as
part of the macro substitution process (macros are also typically represented with uppercase
letters).
4.9.2 Naming Files
Naming files should follow the same guidelines as naming identifiers with a few additions.
AV Rule 53
Header files will always have a file name extension of ".h".
AV Rule 53.1
The following character sequences shall not appear in header file names: ‘, \, /*, //, or ".
Rationale: If any of the character sequences ‘, \, /*, //, or " appears in a header file name (i.e.
<h-char-sequence>), the resulting behavior is undefined. [10], 2.8(2) Note that relative
pathnames may be used. However, only “/” may be used to separate directory and file names.
Examples:
#include <foo /* comment */ .h> // Bad: “/*” prohibited
#include <foo’s .h> // Bad: “’” prohibited
#include <dir1\dir2\foo.h> // Bad: “\” prohibited
#include <dir1/dir2/foo.h> // Good: relative path used

AV Rule 54
Implementation files will always have a file name extension of ".cpp".
AV Rule 55
The name of a header file should reflect the logical entity for which it provides declarations.
Example:
For the Matrix entity, the header file would be named:
Matrix.h
AV Rule 56
The name of an implementation file should reflect the logical entity for which it provides
definitions and have a “.cpp” extension (this name will normally be identical to the header
file that provides the corresponding declarations.)
At times, more than one .cpp file for a given logical entity will be required. In these cases, a
suffix should be appended to reflect a logical differentiation.
Example 1: One .cpp file for the Matrix class:
Matrix.cpp
Example 2: Multiple files for a math library:
Math_sqrt.cpp
Math_sin.cpp
Math_cos.cpp
4.9.3 Classes
AV Rule 57
The public, protected, and private sections of a class will be declared in that order (the public
section is declared before the protected section which is declared before the private section).
Rationale: By placing the public section first, everything that is of interest to a user is
gathered in the beginning of the class definition. The protected section may be of interest to
designers when considering inheriting from the class. The private section contains details that
should be of the least general interest.
4.9.4 Functions
AV Rule 58
When declaring and defining functions with more than two parameters, the leading
parenthesis and the first argument will be written on the same line as the function name.
Each additional argument will be written on a separate line (with the closing parenthesis
directly after the last argument).
Rationale: Readability and style. See AV Rule 58 in Appendix A for examples.

4.9.5 Blocks
AV Rule 59 (MISRA Rule 59, Revised)
The statements forming the body of an if, else if, else, while, do…while or for statement shall
always be enclosed in braces, even if the braces form an empty block.
Rationale: Readability. It can be difficult to see “;” when it appears by itself. See AV Rule
59 in Appendix A for examples.
AV Rule 60
Braces ("{}") which enclose a block will be placed in the same column, on separate lines
directly before and after the block.
Example:
if (var_name == true)
{
}
else
{
}
AV Rule 61
Braces ("{}") which enclose a block will have nothing else on the line except comments (if
necessary).
4.9.6 Pointers and References
AV Rule 62
The dereference operator ‘*’ and the address-of operator ‘&’ will be directly connected with
the type-specifier.
Rationale: The int32* p; form emphasizes type over syntax while the int32 *p; form
emphasizes syntax over type. Although both forms are equally valid C++, the heavy
emphasis on types in C++ suggests that int32* p; is the preferable form.
Examples:
int32* p; // Correct
int32 *p; // Incorrect
int32* p, q; // Probably error. However, this declaration cannot occur
// under the one name per declaration style required by AV Rule 152.
4.9.7 Miscellaneous
AV Rule 63
Spaces will not be used around ‘.’ or ‘->’, nor between unary operators and operands.
Rationale: Readability and style.

4.10 Classes
4.10.1 Class Interfaces
AV Rule 64
A class interface should be complete and minimal. See Meyers [6], item 18.
Rationale: A complete interface allows clients to do anything they may reasonably want to
do. On the other hand, a minimal interface will contain as few functions as possible (i.e. no
two functions will provide overlapping services). Hence, the interface will be no more
complicated than it has to be while allowing clients to perform whatever activities are
reasonable for them to expect.
Note: Overlapping services may be required where efficiency requirements dictate. Also, the
use of helper functions (Stroustrup [2], 10.3.2) can simplify class interfaces.
4.10.2 Considerations Regarding Access Rights
Roughly two types of classes exist: those that essentially aggregate data and those that provide
an abstraction while maintaining a well-defined state or invariant. The following rules provide
guidance in this regard.
AV Rule 65
A structure should be used to model an entity that does not require an invariant.
AV Rule 66
A class should be used to model an entity that maintains an invariant.
AV Rule 67
Public and protected data should only be used in structs—not classes.
Rationale: A class is able to maintain its invariant by controlling access to its data. However,
a class cannot control access to its members if those members non-private. Hence all data in
a class should be private.
Exception: Protected members may be used in a class as long as that class does not
participate in a client interface. See AV Rule 88.
4.10.3 Member Functions
AV Rule 68
Unneeded implicitly generated member functions shall be explicitly disallowed. See Meyers
[6], item 27.
Rationale: Eliminate any surprises that may occur as a result of compiler generated
functions. For example, if the assignment operator is unneeded for a particular class, then it
should be declared private (and not defined). Any attempt to invoke the operator will result
in a compile-time error. On the contrary, if the assignment operator is not declared, then
when it is invoked, a compiler-generated form will be created and subsequently executed.
This could lead to unexpected results.

Note: If the copy constructor is explicitly disallowed, the assignment operator should be as
well.)
4.10.4 const Member Functions
AV Rule 69
A member function that does not affect the state of an object (its instance variables) will be
declared const.
Member functions should be const by default. Only when there is a clear, explicit reason
should the const modifier on member functions be omitted.
Rationale: Declaring a member function const is a means of ensuring that objects will not be
modified when they should not. Furthermore, C++ allows member functions to be
overloaded on their const-ness.
4.10.5 Friends
AV Rule 70
A class will have friends only when a function or object requires access to the private
elements of the class, but is unable to be a member of the class for logical or efficiency
reasons.
Rationale: The overuse of friends leads to code that is both difficult to understand and
maintain.
AV Rule 70 in Appendix A provides examples of acceptable uses of friends. Note that the
alternative to friendship in some instances is to expose more internal detail than is necessary.
In those cases friendship is not only allowed, but is the preferable option.
4.10.6 Object Lifetime, Constructors, and Destructors
4.10.6.1 Object Lifetime
Conceptually, developers understand that objects should not be used before they have been
created or after they have been destroyed. However, a number of scenarios may arise where this
distinction may not be obvious. Consequently, the following object-lifetime rule is provided to
highlight these instances.
AV Rule 70.1
An object shall not be improperly used before its lifetime begins or after its lifetime ends.
Rationale: Improper use of an object, before it is created or after it is destroyed, results in
undefined behavior. See section 3.8 of [10] for details on “proper” vs. “improper” use. See
also AV Rule 70.1 in Appendix A for examples.

4.10.6.2 Constructors
AV Rule 71
Calls to an externally visible operation of an object, other than its constructors, shall not be
allowed until the object has been fully initialized.
Rationale: Avoid problems resulting from incomplete object initialization. Further details
are given in AV Rule 71 in Appendix A.
AV Rule 71.1
A class’s virtual functions shall not be invoked from its destructor or any of its constructors.
Rationale: A class’s virtual functions are resolved statically (not dynamically) in its
constructors and destructor. See AV Rule 71.1 in Appendix_A for additional details.
AV Rule 72
The invariant2 for a class should be:
• a part of the postcondition of every class constructor,
• a part of the precondition of the class destructor (if any),
• a part of the precondition and postcondition of every other publicly accessible
operation.
Rationale: Prohibit clients from influencing the invariant of an object through any other
means than the public interface.
AV Rule 73
Unnecessary default constructors shall not be defined. See Meyers [7], item 4. (See also AV
Rule 143).
Rationale: Discourage programmers from creating objects until the requisite data is
available for complete object construction (i.e. prevent objects from being created in a
partially initialized state). See AV Rule 73 in Appendix A for examples.
AV Rule 74
Initialization of nonstatic class members will be performed through the member initialization
list rather than through assignment in the body of a constructor. See Meyers [6], item 12.
Exception: Assignment should be used when an initial value cannot be represented by a
simple expression (e.g. initialization of array values), or when a name must be introduced
before it can be initialized (e.g. value received via an input stream).
See AV Rule 74 in Appendix A for details.
2 A class invariant is a statement-of-fact about a class that must be true for all stable instances of the class. A class is
considered to be in a stable state immediately after construction, immediately before destruction, and immediately
before and after any remote public method invocation.

AV Rule 75
Members of the initialization list shall be listed in the order in which they are declared in the
class. See Stroustrup [2], 10.4.5 and Meyers [6], item 13.
Note: Since base class members are initialized before derived class members, base class
initializers should appear at the beginning of the member initialization list.
Rationale: Members of a class are initialized in the order in which they are declared—not
the order in which they appear in the initialization list.
AV Rule 76
A copy constructor and an assignment operator shall be declared for classes that contain
pointers to data items or nontrivial destructors. See Meyers [6], item 11.
Note: See also AV Rule 80 which indicates that default copy and assignment operators are
preferable when those operators offer reasonable semantics.
Rationale: Ensure resources are appropriately managed during copy and assignment
operations. See AV Rule 76 in Appendix A for additional details.
AV Rule 77
A copy constructor shall copy all data members and bases that affect the class invariant (a
data element representing a cache, for example, would not need to be copied).
Note: If a reference counting mechanism is employed by a class, a literal copy need not be
performed in every case. See also AV Rule 83.
Rationale: Ensure data members and bases are properly handled when an object is copied.
See AV Rule 77 in Appendix A for additional details.
AV Rule 77.1
The definition of a member function shall not contain default arguments that produce a
signature identical to that of the implicitly-declared copy constructor for the corresponding
class/structure.
Rationale: Compilers are not required to diagnose this ambiguity. See AV Rule 77.1 in
Appendix A for additional details.
4.10.6.3 Destructors
AV Rule 78
All base classes with a virtual function shall define a virtual destructor.
Rationale: Prevent undefined behavior. If an application attempts to delete a derived class
object through a base class pointer, the result is undefined if the base class’s destructor is
non-virtual.
Note: This rule does not imply the use of dynamic memory (allocation/deallocation from the
free store) will be used. See AV Rule 206.

AV Rule 79
All resources acquired by a class shall be released by the class’s destructor. See Stroustrup
[2], 14.4 and Meyers [7], item 9.
Rationale: Prevention of resource leaks, especially in error cases. See AV Rule 79 in
Appendix A for additional details.
4.10.7 Assignment Operators
AV Rule 80
The default copy and assignment operators will be used for classes when those operators
offer reasonable semantics.
Rationale: The default versions are more likely to be correct, easier to maintain and efficient
than that generated by hand.
AV Rule 81
The assignment operator shall handle self-assignment correctly (see Stroustrup [2],
Appendix E.3.3 and 10.4.4)
Rationale: a = a; must function correctly. See AV Rule 81 in Appendix A for examples.
AV Rule 82
An assignment operator shall return a reference to *this.
Rationale: Both the standard library types and the built-in types behave in this manner. See
AV Rule 81 for an example of an assignment operator overload.
AV Rule 83
An assignment operator shall assign all data members and bases that affect the class invariant
(a data element representing a cache, for example, would not need to be copied).
Note: To correctly copy a stateful virtual base in a portable manner, it must hold that if x1
and x2 are objects of virtual base X, then x1=x2; x1=x2; must be semantically
equivalent to x1=x2; [10] 12.8(13)
Rationale: Ensure data members and bases are properly handled under assignment. See AV
Rule 83 in Appendix A for additional details. See also AV Rule 77.
4.10.8 Operator Overloading
AV Rule 84
Operator overloading will be used sparingly and in a conventional manner.
Rationale: Since unconventional or inconsistent uses of operator overloading can easily lead
to confusion, operator overloads should only be used to enhance clarity and should follow the
natural meanings and conventions of the language. For instance, a C++ operator "+=" shall
have the same meaning as "+" and "=".

AV Rule 85
When two operators are opposites (such as == and !=), both will be defined and one will be
defined in terms of the other.
Rationale: If operator==() is supplied, then one could reasonable expect that operator!=()
would be supplied as well. Furthermore, defining one in terms of the other simplifies
maintenance. See AV Rule 85 in Appendix A for an example.
4.10.9 Inheritance
Class hierarchies are appropriate when run-time selection of implementation is required. If
run-time resolution is not required, template parameterization should be considered
(templates are better-behaved and faster than virtual functions). Finally, simple independent
concepts should be expressed as concrete types. The method selected to express the solution
should be commensurate with the complexity of the problem.
The following rules provide additional detail and guidance when considering the structure of
inheritance hierarchies.
AV Rule 86
Concrete types should be used to represent simple independent concepts. See Stroustrup [2],
25.2.
Rationale: Well designed concrete classes tend to be efficient in both space and time, have
minimal dependencies on other classes, and tend to be both comprehensible and usable in
isolation.
AV Rule 87
Hierarchies should be based on abstract classes. See Stroustrup [2], 12.5.
Rationale: Hierarchies based on abstract classes tend to focus designs toward producing
clean interfaces, keep implementation details out of interfaces, and minimize compilation
dependencies while allowing alternative implementations to coexist. See AV Rule 87 in
Appendix A for examples.
AV Rule 88
Multiple inheritance shall only be allowed in the following restricted form: n interfaces plus
m private implementations, plus at most one protected implementation.
Rationale: Multiple inheritance can lead to complicated inheritance hierarchies that are
difficult to comprehend and maintain.
See AV Rule 88 in Appendix A for examples of both appropriate and inappropriate uses of
multiple inheritance.

AV Rule 88.1
A stateful virtual base shall be explicitly declared in each derived class that accesses it.
Rationale: Explicitly declaring a stateful virtual base at each level in a hierarchy (where that
base is used), documents that fact that no assumptions can be made with respect to the
exclusive use of the data contained within the virtual base. See AV Rule 88.1 in Appendix A
for additional details.
AV Rule 89
A base class shall not be both virtual and non-virtual in the same hierarchy.
Rationale: Hierarchy becomes difficult to comprehend and use.
AV Rule 90
Heavily used interfaces should be minimal, general and abstract. See Stroustrup [2] 23.4.
Rationale: Enable interfaces to exhibit stability in the face of changes to their hierarchies.
AV Rule 91
Public inheritance will be used to implement “is-a” relationships. See Meyers [6], item 35.
Rationale: Public inheritance and private inheritance mean very different things in C++ and
should therefore be used accordingly. Public inheritance implies an “is-a” relationship. That
is, every object of a publicly derived class D is also an object of the base type B, but not vice
versa. Moreover, type B represents a more general concept than type D, and type D
represents a more specialized concept than type B. Thus, stating that D publicly inherits from
B, is an assertion that D is a subtype of B. That is, objects of type D may be used anywhere
that objects of type B may be used (since an object of type D is really an object of type B as
well).
In contrast to public inheritance, private and protected inheritance means “is-implemented-
in-terms-of”. It is purely an implementation technique—the interface is ignored. See also AV
Rule 93.

AV Rule 92
A subtype (publicly derived classes) will conform to the following guidelines with respect to
all classes involved in the polymorphic assignment of different subclass instances to the same
variable or parameter during the execution of the system:
• Preconditions of derived methods must be at least as weak as the preconditions of the
methods they override.
• Postconditions of derived methods must be at least as strong as the postconditions of
the methods they override.
In other words, subclass methods must expect less and deliver more than the base class
methods they override. This rule implies that subtypes will conform to the Liskov
Substitution Principle.
Rationale: Predictable behavior of derived classes when used within base class contexts. See
AV Rule 92 in Appendix A for additional details.
AV Rule 93
“has-a” or “is-implemented-in-terms-of” relationships will be modeled through membership
or non-public inheritance. See Meyers [6], item 40.
Rationale: Public inheritance means “is-a” (see AV Rule 91) while nonpublic inheritance
means “has-a” or “is-implemented-in-terms-of”. See AV Rule 93 in Appendix A for
examples.
AV Rule 94
An inherited nonvirtual function shall not be redefined in a derived class. See Meyers [6],
item 37.
Rationale: Prevent an object from exhibiting “two-faced” behavior. See AV Rule 94 in
Appendix A for an example.
AV Rule 95
An inherited default parameter shall never be redefined. See Meyers [6], item 38.
Rationale: The redefinition of default parameters for virtual functions often produces
surprising results. See AV Rule 95 in Appendix A for an example.
AV Rule 96
Arrays shall not be treated polymorphically. See Meyers [7], item 3.
Rationale: Array indexing in C/C++ is implemented as pointer arithmetic. Hence, a[i] is
equivalent to a+i*SIZEOF(array element). Since derived classes are often larger than base
classes, polymorphism and pointer arithmetic are not compatible techniques.

AV Rule 97
Arrays shall not be used in interfaces. Instead, the Array class should be used.
Rationale: Arrays degenerate to pointers when passed as parameters. This “array decay”
problem has long been known to be a source of errors.
Note: See Array.doc for guidance concerning the proper use of the Array class, including its
interaction with memory management and error handling facilities.
4.10.10Virtual Member Functions
AV Rule 97.1
Neither operand of an equality operator (== or !=) shall be a pointer to a virtual member
function.
Rationale: If either operand of an equality operator (== or !=) is a pointer to a virtual
member function, the result is unspecified [10], 5.10(2).
Several other sections have also touched on virtual member functions and polymorphism. Hence,
the following cross references are provided so that these rules may be accessed from a single
location: AV Rule 71, AV Rule 78, AV Rule 87-AV Rule 97, and AV Rule 221.

4.11 Namespaces
AV Rule 98
Every nonlocal name, except main(), should be placed in some namespace. See Stroustrup
[2], 8.2.
Rationale: Avoid name clashes in large programs with many parts.
AV Rule 99
Namespaces will not be nested more than two levels deep.
Rationale: Simplicity and clarity. Deeply nested namespaces can be difficult to comprehend
and use correctly.
AV Rule 100
Elements from a namespace should be selected as follows:
• using declaration or explicit qualification for few (approximately five) names,
• using directive for many names.
Rationale: All elements in a namespace need not be pulled in if only a few elements are
actually needed.

4.12 Templates
Templates provide a powerful technique for creating families of functions or classes
parameterized by type. As a result, generic components may be created that match corresponding
hand-written versions in both size and performance [2].
Although template techniques have proven to be both powerful and expressive, it may be unclear
when to prefer the use of templates over the use of inheritance. The following guidelines
provided by Stroustrup[2], 13.8, offer advice in this regard:
1. Prefer a template over derived classes when run-time efficiency is at a premium.
2. Prefer derived classes over a template if adding new variants without recompilation is
important.
3. Prefer a template over derived classes when no common base can be defined.
4. Prefer a template over derived classes when built-in types and structures with
compatibility constraints are important.
AV Rule 101
Templates shall be reviewed as follows:
1. with respect to the template in isolation considering assumptions or requirements
placed on its arguments.
2. with respect to all functions instantiated by actual arguments.
Note: The compiler should be configured to generate the list of actual template
instantiations. See AV Rule 101 in Appendix A for an example.
Rationale: Since many instantiations of a template can be generated, any review should
consider all actual instantiations as well as any assumptions or requirements placed on
arguments of instantiations.
AV Rule 102
Template tests shall be created to cover all actual template instantiations.
Note: The compiler should be configured to generate the list of actual template
instantiations. See AV Rule 102 in Appendix A for an example.
Rationale: Since many instantiations of a template can be generated, test cases should be
created to cover all actual instantiations.
AV Rule 103
Constraint checks should be applied to template arguments.
Rationale: Explicitly capture parameter constraints in code as well as produce
comprehensible error messages. See AV Rule 103 in Appendix A for examples.
AV Rule 104
A template specialization shall be declared before its use. See Stroustrup [2], 13.5.
Rationale: C++ language rule. The specialization must be in scope for every use of the type
for which it is specialized.

Example:
template<class T> class List {…};
List<int32*> li;
template<class T> class List<T*> {…}; //Error: this specialization should be used for li
// in the previous statement.
AV Rule 105
A template definition’s dependence on its instantiation contexts should be minimized. See
Stroustrup [2], 13.2.5 and C.13.8.
Rationale: Since templates are likely to be instantiated in multiple contexts with different
parameter types, any nonlocal dependencies will increase the likelihood that errors or
incompatibilities will eventually surface.
AV Rule 106
Specializations for pointer types should be made where appropriate. See Stroustrup [2], 13.5.
Rationale: Pointer types often require special semantics or provide special optimization
opportunities.
4.13 Functions
4.13.1 Function Declaration, Definition and Arguments
AV Rule 107 (MISRA Rule 68)
Functions shall always be declared at file scope.
Rationale: Declaring functions at block scope may be confusing.
AV Rule 108 (MISRA Rule 69)
Functions with variable numbers of arguments shall not be used.
Rationale: The variable argument feature is difficult to use in a type-safe manner (i.e.
typical language checking rules aren’t applied to the additional parameters).
Note: In some cases, default arguments and overloading are alternatives to the variable
arguments feature. See AV Rule 108 in Appendix A for an example.
AV Rule 109
A function definition should not be placed in a class specification unless the function is
intended to be inlined.
Rationale: Class specifications are less compact and more difficult to read when they
include implementations of member functions. Consequently, it is often preferable to place
member function implementations in a separate file. However, including the implementation
in the specification instructs the compiler to inline the method (if possible). Since inlining
short functions can save both time and space, functions intended to be inlined may appear in
the class specification. See AV Rule 109 in Appendix A for an example.

AV Rule 110
Functions with more than 7 arguments will not be used.
Rationale: Functions having long argument lists can be difficult to read, use, and maintain.
Functions with too many parameters may indicate an under use of objects and abstractions.
Exception: Some constructors may require more than 7 arguments. However, one should
consider if abstractions are being underused in this scenario.
AV Rule 111
A function shall not return a pointer or reference to a non-static local object.
Rationale: After return, the local object will no longer exist.
AV Rule 112
Function return values should not obscure resource ownership.
Rationale: Potential source of resource leaks. See AV Rule 173 and AV Rule 112 in
Appendix A for examples.
4.13.2 Return Types and Values
AV Rule 113 (MISRA Rule 82, Revised)
Functions will have a single exit point.
Rationale: Numerous exit points tend to produce functions that are both difficult to
understand and analyze.
Exception: A single exit is not required if such a structure would obscure or otherwise
significantly complicate (such as the introduction of additional variables) a function’s control
logic. Note that the usual resource clean-up must be managed at all exit points.
AV Rule 114 (MISRA Rule 83, Revised)
All exit points of value-returning functions shall be through return statements.
Rationale: Flowing off the end of a value-returning function results in undefined behavior.
AV Rule 115 (MISRA Rule 86)
If a function returns error information, then that error information will be tested.
Rationale: Ignoring return values could lead to a situation in which an application continues
processing under the false assumption that the context in which it is operating (or the item on
which it is operating) is valid.

4.13.3 Function Parameters (Value, Pointer or Reference)
AV Rule 116
Small, concrete-type arguments (two or three words in size) should be passed by value if
changes made to formal parameters should not be reflected in the calling function.
Rationale: Pass-by-value is the simplest, safest method for small objects of concrete type.
Note that non-concrete objects must be passed by pointer or reference to realize polymorphic
behavior. See rules AV Rule 117 and AV Rule 118.
AV Rule 117
Arguments should be passed by reference if NULL values are not possible:
AV Rule 117.1 An object should be passed as const T& if the function should not change
the value of the object.
AV Rule 117.2 An object should be passed as T& if the function may change the value of
the object.
Rationale: Since references cannot be NULL, checks for NULL values will be eliminated
from the code. Furthermore, references offer a more convenient notation than pointers.
AV Rule 118
Arguments should be passed via pointers if NULL values are possible:
AV Rule 118.1 An object should be passed as const T* if its value should not be modified.
AV Rule 118.2 An object should be passed as T* if its value may be modified.
Rationale: References cannot be NULL.
4.13.4 Function Invocation
AV Rule 119 (MISRA Rule 70)
Functions shall not call themselves, either directly or indirectly (i.e. recursion shall not be
allowed).
Rationale: Since stack space is not unlimited, stack overflows are possible.
Exception: Recursion will be permitted under the following circumstances:
1. development of SEAL 3 or general purpose software, or
2. it can be proven that adequate resources exist to support the maximum level of
recursion possible.

4.13.5 Function Overloading
AV Rule 120
Overloaded operations or methods should form families that use the same semantics, share
the same name, have the same purpose, and that are differentiated by formal parameters.
Rationale: Inconsistent use of overloading can lead to considerable confusion. See AV Rule
120 in Appendix A for examples.
4.13.6 Inline Functions
Inline functions often offer a speed advantage over traditional functions as they do not
require the typical function call overhead. Functions are typically inlined when either the
function definition is included in the class declaration or the keyword inline precedes the
function definition.
Example A: Inlined since definition is Example B: Inlined because of the inline
included in declaration. keyword
class Sample_class int32 foo (void);
{
public: inline int foo (void)
int32 get_data (void) {
{ …
return data; }
}
};
The C++ standard [10] provides the following information in regards to the use of inline
functions. These observations are not listed as AV Rules since they are C++ language rules.
1. An inline function shall be defined in every translation unit in which it is used and shall
have exactly the same definition in every case. (Note this observation implies that inline
function definitions should be included in header files.)
2. If a function with external linkage is declared inline in one translation unit, it shall be
declared inline in all translation units in which it appears; no diagnostic is required.
3. An inline function with external linkage shall have the same address in all translation
units.
4. A static local variable in an extern inline function always refers to the same object.
5. A string literal in an extern inline function is the same object in different translation units.
AV Rule 121
Only functions with 1 or 2 statements should be considered candidates for inline functions.
Rationale: The compiler is not compelled to actually make a function inline. Decision
criteria differ from one compiler to another. The keyword inline is simply a request for the
compiler to inline the function. The compiler is free to ignore this request and make a real
function call. See AV Rule 121 in Appendix A for additional details.

AV Rule 122
Trivial accessor and mutator functions should be inlined.
Rationale: Inlining short, simple functions can save both time and space. See AV Rule 122
in Appendix A for an example.
AV Rule 123
The number of accessor and mutator functions should be minimized.
Rationale: Numerous accessors and mutators may indicate that a class simply serves to
aggregate a collection of data rather than to embody an abstraction with a well-defined state
or invariant. In this case, a struct with public data may be a better alternative (see section
4.10.2, AV Rule 65, and AV Rule 66).
AV Rule 124
Trivial forwarding functions should be inlined.
Rationale: Inlining short, simple functions can save both time and space.
4.13.7 Temporary Objects
AV Rule 125
Unnecessary temporary objects should be avoided. See Meyers [7], item 19, 20, 21.
Rationale: Since the creation and destruction of temporary objects that are either large or
involve complicated constructions can result in significant performance penalties, they
should be avoided. See AV Rule 125 in Appendix A for additional details.
4.14 Comments
Comments in header files are meant for the users of classes and functions, while comments in
implementation files are meant for those who maintain the classes.
Comments are often said to be either strategic or tactical. A strategic comment describes
what a function or section of code is intended to do, and is placed before the code. A tactical
comment describes what a single line of code is intended to do. Unfortunately, too many
tactical comments can make code unreadable. For this reason, comments should be primarily
strategic, unless trying to explain very complicated code (i.e. one should avoid stating in a
comment what is clearly stated in code).
AV Rule 126
Only valid C++ style comments (//) shall be used. See AV Rule 126 in Appendix A for
additional details concerning valid C++ style comments.
Rationale: A single standard provides consistency throughout the code.
Exception: Automatic code generators that cannot be configured to use the “//” form.

AV Rule 127
Code that is not used (commented out) shall be deleted.
Rationale: No dead code is allowed.
Exception: Code that is simply part of an explanation may appear in comments.
AV Rule 128
Comments that document actions or sources (e.g. tables, figures, paragraphs, etc.) outside of
the file being documented will not be allowed.
Rationale: The comments in a file should require changes only when changes are necessary
to the file itself. Note that this rule does not preclude the documentation of valid assumptions
that may made be entities contained within the file.
AV Rule 129
Comments in header files should describe the externally visible behavior of the functions or
classes being documented.
Rationale: Exposing the internal workings of functions or classes to clients might enable
those clients to create dependences on the internal representations.
AV Rule 130
The purpose of every line of executable code should be explained by a comment, although
one comment may describe more than one line of code.
Rationale: Readability. Every line of code should be represented by a comment. However,
this rule does not say that every line of code should have a comment; a comment might
represent more than one source line of code.
AV Rule 131
One should avoid stating in comments what is better stated in code (i.e. do not simply repeat
what is in the code).
Rationale: While redundant comments are unnecessary, they also serve to increase the
maintenance effort.
Example: The following example illustrates an unnecessary comment.
a = b+c; // Bad: add b to c and place the result in a.
AV Rule 132
Each variable declaration, typedef, enumeration value, and structure member will be
commented.
Exception: Cases where commenting would be unnecessarily redundant.

AV Rule 133
Every source file will be documented with an introductory comment that provides
information on the file name, its contents, and any program-required information (e.g. legal
statements, copyright information, etc).
AV Rule 134
Assumptions (limitations) made by functions should be documented in the function’s
preamble.
Rationale: Maintenance efforts become very difficult if the assumptions (limitations) upon
which functions are built are unknown.
4.15 Declarations and Definitions
AV Rule 135 (MISRA Rule 21, Revised)
Identifiers in an inner scope shall not use the same name as an identifier in an outer scope,
and therefore hide that identifier.
Rationale: Hiding identifiers can be very confusing.
Example:
int32 sum = 0;
{
int32 sum = 0; // Bad: hides sum in outer scope.
…
sum = f (x);
}
AV Rule 136 (MISRA Rule 22, Revised)
Declarations should be at the smallest feasible scope. (See also AV Rule 143).
Rationale: This rule attempts to minimize the number of live variables that must be
simultaneously considered. Furthermore, variable declarations should be postponed until
enough information is available for full initialization (i.e. a variable should never be placed in
a partly-initialized or initialized-but-not-valid state.) See AV Rule 136 in Appendix A for
examples.
AV Rule 137 (MISRA Rule 23)
All declarations at file scope should be static where possible.
Rationale: Minimize dependencies between translation units where possible. See AV Rule
137 in Appendix A for additional details.
AV Rule 138 (MISRA Rule 24)
Identifiers shall not simultaneously have both internal and external linkage in the same
translation unit.
Rationale: Avoid variable-name hiding which can be confusing. See AV Rule 138 in
Appendix A for further details.

AV Rule 139 (MISRA Rule 27)
External objects will not be declared in more than one file. (See also AV Rule 39.)
Rationale: Avoid inconsistent declarations. See AV Rule 139 in Appendix A for further
details.
Note: This type of error will be caught by linkers, but typically later than is desired (i.e. the
inconsistency could exist in a different group’s build.) Normally this will mean
declaring external objects in header files which will then be included in all other files
that need to use those objects (including the files which define them).
AV Rule 140 (MISRA Rule 28, Revised)
The register storage class specifier shall not be used.
Rationale: Compiler technology is now capable of optimal register placement.
AV Rule 141
A class, structure, or enumeration will not be declared in the definition of its type.
Rationale: Readability. See AV Rule 141 in Appendix A for examples.
4.16 Initialization
AV Rule 142 (MISRA Rule 30, Revised)
All variables shall be initialized before use. (See also AV Rule 136, AV Rule 71, and AV
Rule 73, and AV Rule 143 concerning declaration scope, object construction, default
constructors, and the point of variable introduction respectively.)
Rationale: Prevent the use of variables before they have been properly initialized. See AV
Rule 142 in Appendix A for additional information.
Exception: Exceptions are allowed where a name must be introduced before it can be
initialized (e.g. value received via an input stream).
AV Rule 143
Variables will not be introduced until they can be initialized with meaningful values. (See
also AV Rule 136, AV Rule 142, and AV Rule 73 concerning declaration scope,
initialization before use, and default constructors respectively.)
Rationale: Prevent clients from accessing variables without meaningful values. See AV Rule
143 in Appendix A for examples.
AV Rule 144 (MISRA Rule 31)
Braces shall be used to indicate and match the structure in the non-zero initialization of
arrays and structures.
Rationale: Readability.
Example:
int32 a[2][2] = { {0,1} ,{2,3} };

AV Rule 145 (MISRA Rule 32 )
In an enumerator list, the ‘=‘ construct shall not be used to explicitly initialize members
other than the first, unless all items are explicitly initialized.
Rationale: Mixing the automatic and manual allocation of enumerator values is error-prone.
Note that exceptions are allowed for clearly-defined standard conventions. See AV Rule 145
in Appendix A for additional details.
4.17 Types
AV Rule 146 (MISRA Rule 15)
Floating point implementations shall comply with a defined floating point standard.
The standard that will be used is the ANSI/IEEE Std 754 [1].
Rationale: Consistency.
AV Rule 147 (MISRA Rule 16)
The underlying bit representations of floating point numbers shall not be used in any way by
the programmer.
Rationale: Manipulating bits is error prone. See AV Rule 147 in Appendix A for additional
details.
AV Rule 148
Enumeration types shall be used instead of integer types (and constants) to select from a
limited series of choices.
Note: This rule is not intended to exclude character constants (e.g. ‘A’, ‘B’, ‘C’, etc.) from
use as case labels.
Rationale: Enhances debugging, readability and maintenance. Note that a compiler flag (if
available) should be set to generate a warning if all enumerators are not present in a switch
statement.
4.18 Constants
Section 4.6.2 contains additional details concerning constants and the use of enum and
#define.
AV Rule 149 (MISRA Rule 19)
Octal constants (other than zero) shall not be used.
Rationale: Any integer constant beginning with a zero (‘0’) is defined by the C++ standard
to be an octal constant. Due to the confusion this causes, octal constants should be avoided.
Note: Hexadecimal numbers and zero (which is also an octal constant) are allowed.
AV Rule 150
Hexadecimal constants will be represented using all uppercase letters.

AV Rule 151
Numeric values in code will not be used; symbolic values will be used instead.
Rationale: Improved readability and maintenance.
Exception: A class/structure constructor may initialize an array member with numeric
values.
class A
{
A()
{
coefficient[0] = 1.23; // Good
coefficient[1] = 2.34; // Good
coefficient[2] = 3.45; // Good
}
private:
float64 coefficient[3]; // Cannot be initialized via the member initialization list.
};
Note: In many cases ‘0’ and ‘1’ are not magic numbers but are part of the fundamental logic
of the code (e.g. ‘0’ often represents a NULL pointer). In such cases, ‘0’ and ‘1’ may
be used.
AV Rule 151.1
A string literal shall not be modified.
Note that strictly conforming compilers should catch violations, but many do not.
Rationale: The effect of attempting to modify a string literal is undefined [10], 2.13.4(2).
See also AV Rule 151.1 in Appendix A for additional details.
4.19 Variables
AV Rule 152
Multiple variable declarations shall not be allowed on the same line.
Rationale: Increases readability and prevents confusion (see also AV Rule 62).
Example:
int32* p, q; // Probably error.
int32 first button_on_top_of_the_left_box, i; // Bad: Easy to overlook i

4.20 Unions and Bit Fields
AV Rule 153 (MISRA Rule 110, Revised)
Unions shall not be used.
Rationale: Unions are not statically type-safe and are historically known to be a source of
errors.
Note: In some cases, derived classes and virtual functions may be used as an alternative to
unions.
AV Rule 154 (MISRA Rules 111 and 112, Revised)
Bit-fields shall have explicitly unsigned integral or enumeration types only.
Rationale: Whether a plain (neither explicitly signed nor unsigned) char, short, int or long
bit-field is signed or unsigned is implementation-defined.[10] Thus, explicitly declaring a
bit-filed unsigned prevents unexpected sign extension or overflow.
Note: MISRA Rule 112 no longer applies since it discusses a two-bit minimum-length
requirement for bit-fields of signed types.
AV Rule 155
Bit-fields will not be used to pack data into a word for the sole purpose of saving space.
Note: Bit-packing should be reserved for use in interfacing to hardware or conformance to
communication protocols.
Warning: Certain aspects of bit-field manipulation are implementation-defined.
Rationale: Bit-packing adds additional complexity to the source code. Moreover, bit-packing
may not save any space at all since the reduction in data size achieved through packing is
often offset by the increase in the number of instructions required to pack/unpack the data.
AV Rule 156 (MISRA Rule 113)
All the members of a structure (or class) shall be named and shall only be accessed via their
names.
Rationale: Reading/writing to unnamed locations in memory is error prone.
Exception: An unnamed bit-field of width zero may be used to specify alignment of the next
bit-field at an allocation boundary. [10], 9.6(2)

4.21 Operators
AV Rule 157 (MISRA Rule 33)
The right hand operand of a && or || operator shall not contain side effects.
Rationale: Readability. The conditional evaluation of the right-hand side could be
overlooked. See AV Rule 157 in Appendix A for an example.
AV Rule 158 (MISRA Rule 34)
The operands of a logical && or || shall be parenthesized if the operands contain binary
operators.
Rationale: Readability. See AV Rule 158 in Appendix A for examples.
AV Rule 159
Operators ||, &&, and unary & shall not be overloaded. See Meyers [7], item 7.
Rationale: First, the behavior of the || and && operators depend on short-circuit evaluation
of the operands. However, short-circuit evaluation is not possible for overloaded versions of
the || and && operators. Hence, overloading these operators may produce unexpected results.
Next, if the address of an object of incomplete class type is taken, but the complete form of
the type declares operator&() as a member function, the resulting behavior is undefined. [10]
AV Rule 160 (MISRA Rule 35, Modified)
An assignment expression shall be used only as the expression in an expression statement.
Rationale: Readability. Assignment (=) may be easily confused with the equality (==). See
AV Rule 160 in Appendix A for examples.
AV Rule 162
Signed and unsigned values shall not be mixed in arithmetic or comparison operations.
Rationale: Mixing signed and unsigned values is error prone as it subjects operations to
numerous arithmetic conversion and integral promotion rules.
AV Rule 163
Unsigned arithmetic shall not be used.
Rationale: Over time, unsigned values will likely be mixed with signed values thus violating
AV Rule 162.
AV Rule 164 (MISRA Rule 38)
The right hand operand of a shift operator shall lie between zero and one less than the width
in bits of the left-hand operand (inclusive).
Rationale: If the right operand is either negative or greater than or equal to the length in bits
of the promoted left operand, the result is undefined. [10]

AV Rule 164.1
The left-hand operand of a right-shift operator shall not have a negative value.
Rationale: For e >> e , if e has a signed type and a negative value, the value of (e >> e ) is
1 2 1 1 2
implementation-defined. [10]
AV Rule 165 (MISRA Rule 39)
The unary minus operator shall not be applied to an unsigned expression.
AV Rule 166 (MISRA Rule 40)
The sizeof operator will not be used on expressions that contain side effects.
Rationale: Clarity. The side-effect will not be realized since sizeof only operates on the type
of an expression: the expression itself will not be evaluated.
AV Rule 167 (MISRA Rule 41)
The implementation of integer division in the chosen compiler shall be determined,
documented and taken into account.
Rationale: If one or more of the operands of an integer division is negative, the sign of the
remainder is implementation defined. [10]
Note: For the Green Hills PowerPC C++ compiler, the sign of the remainder is the same as
that of the first operand. Also the quotient is rounded toward zero.
AV Rule 168 (MISRA Rule 42, Revised)
The comma operator shall not be used.
Rationale: Readability. See AV Rule 168 in Appendix A for additional details.
4.22 Pointers & References
AV Rule 169
Pointers to pointers should be avoided when possible.
Rationale: Pointers to pointers are a source of bugs and result in obscure code. Containers or
some other form of abstraction should be used instead (see AV Rule 97).
AV Rule 170 (MISRA Rule 102, Revised)
More than 2 levels of pointer indirection shall not be used.
Rationale: Multiple levels of pointer indirections typically produce code that is difficult to
read, understand and maintain.
Note: This rule leaves no room for using more than 2 levels of pointer indirection. The
word “shall” replaces the word “should” in MISRA Rule 102.

AV Rule 171 (MISRA Rule 103)
Relational operators shall not be applied to pointer types except where both operands are of
the same type and point to:
• the same object,
• the same function,
• members of the same object, or
• elements of the same array (including one past the end of the same array).
Note that if either operand is null, then both shall be null. Also, “members of the same
object” should not be construed to include base class subobjects (See also AV Rule 210).
Rationale: Violations of the above rule may result in unspecified behavior [10], 5.9(2).
AV Rule 173 (MISRA Rule 106, Revised)
The address of an object with automatic storage shall not be assigned to an object which
persists after the object has ceased to exist.
Rationale: An object in a function with automatic storage comes into existence when a
function is called and disappears when the function is exited. Obviously if the object
disappears when the function exits, the address of the object is invalid as well. See Also AV
Rule 111 and AV Rule 112.
AV Rule 174 (MISRA Rule 107)
The null pointer shall not be de-referenced.
Rationale: De-referencing a NULL pointer constitutes undefined behavior. [10] Note that
this often requires that a pointer be checked for non-NULL status before de-referencing
occurs.
AV Rule 175
A pointer shall not be compared to NULL or be assigned NULL; use plain 0 instead.
Rationale: The NULL macro is an implementation-defined C++ null pointer constant that
has been defined in multiple ways including 0, 0L, and (void*)0. Due to C++’s stronger
type-checking, Stroustrup[2] advises the use plain 0 rather than any suggested NULL macro.
AV Rule 176
A typedef will be used to simplify program syntax when declaring function pointers.
Rationale: Improved readability. Pointers to functions can significantly degrade program
readability.

4.23 Type Conversions
AV Rule 177
User-defined conversion functions should be avoided. See Meyers [7], item 5.
Rationale: User-defined conversion functions may be called implicitly in cases where the
programmer may not expect them to be called. See AV Rule 177 in Appendix A for
additional details.
AV Rule 178
Down casting (casting from base to derived class) shall only be allowed through one of the
following mechanism:
• Virtual functions that act like dynamic casts (most likely useful in relatively simple
cases)
• Use of the visitor (or similar) pattern (most likely useful in complicated cases)
Rationale: Casting from a base class to a derived class is unsafe unless some mechanism is
provided to ensure that the cast is legitimate.
Note: Type fields shall not be used as they are too error prone.
Note: Dynamic casts are not allowed at this point due to lack of tool support, but could be
considered at some point in the future after appropriate investigation has been
performed for SEAL1/2 software. Dynamic casts are fine for general purpose
software.
AV Rule 179
A pointer to a virtual base class shall not be converted to a pointer to a derived class.
Rationale: Since the virtualness of inheritance is not a property of a base class, the layout of
a derived class object, referenced through a virtual base pointer, is unknown at compile time.
In essence, this type of downcast cannot be performed safely without the use of a
dynamic_cast or through virtual functions emulating a dynamic_cast.
AV Rule 180 (MISRA Rule 43)
Implicit conversions that may result in a loss of information shall not be used.
Rationale: The programmer may be unaware of the information loss. See AV Rule 180 in
Appendix A for examples.
Note: Templates can be used to resolve many type conversion issues. Also, any compiler
flags that result in warnings for value-destroying conversions should be activated.

AV Rule 181 (MISRA Rule 44)
Redundant explicit casts will not be used.
Rationale: Unnecessary casting clutters the code and could mask later problems if variable
types change over time.
AV Rule 182 (MISRA Rule 45)
Type casting from any type to or from pointers shall not be used.
Rationale: This type of casting can lead to undefined or implementation-defined behavior
(e.g. certain aspects of memory alignments are implementation-defined). Furthermore,
converting a pointer to an integral type can result in the loss of information if the pointer can
represent values larger than the integral type to which it is converted.
Exception 1: Casting from void* to T* is permissible. In this case, static_cast should be
used, but only if it is known that the object really is a T. Furthermore, such code should only
occur in low level memory management routines.
Exception 2: Conversion of literals (i.e. hardware addresses) to pointers.
Device_register input = reinterpret_cast<Device_register>(0XFFA);
AV Rule 183
Every possible measure should be taken to avoid type casting.
Rationale: Errors caused by casts are among the most pernicious, particularly because they
are so hard to recognize. Strict type checking is your friend – take full advantage of it.
AV Rule 184
Floating point numbers shall not be converted to integers unless such a conversion is a
specified algorithmic requirement or is necessary for a hardware interface.
Rationale: Converting a floating-point number to an integer may result in an overflow or
loss of precision. It is acceptable to explicitly cast integers to floating point numbers to
perform mathematical operations (with awareness of the possible real-time impacts as well as
overflow). If this is necessary, the deviation must clearly state how an overflow condition
cannot occur.
AV Rule 185
C++ style casts (const_cast, reinterpret_cast, and static_cast) shall be used instead of the
traditional C-style casts. See Stroustrup [2], 15.4 and Meyers [7], item 2.
Rationale: C-style casts are more dangerous than the C++ named conversion operators since
the C-style casts are difficult to locate in large programs and the intent of the conversion is
not explicit (i.e. (T) e could be a portable conversion between related types, a non-portable
conversion between unrelated types, or a combination of conversions).[0] See AV Rule 185
in Appendix A for additional details.

4.24 Flow Control Structures
AV Rule 186 (MISRA Rule 52)
There shall be no unreachable code.
Note: For reusable template components, unused members will not be included in the object
code.
AV Rule 187 (MISRA Rule 53, Revised)
All non-null statements shall potentially have a side-effect.
Rationale: A non-null statement with no potential side-effect typically indicates a
programming error. See AV Rule 187 in Appendix A for additional information.
AV Rule 188 (MISRA Rule 55, Revised)
Labels will not be used, except in switch statements.
Rationale: Labels are typically either used in switch statements or are as the targets for goto
statements. See exception given in AV Rule 189.
AV Rule 189 (MISRA Rule 56)
The goto statement shall not be used.
Rationale: Frequent use of the goto statement tends to lead to code that is both difficult to
read and maintain.
Exception: A goto may be used to break out of multiple nested loops provided the
alternative would obscure or otherwise significantly complicate the control logic.
AV Rule 190 (MISRA Rule 57)
The continue statement shall not be used.
AV Rule 191 (MISRA Rule 58)
The break statement shall not be used (except to terminate the cases of a switch statement).
Exception: The break statement may be used to “break” out of a single loop provided the
alternative would obscure or otherwise significantly complicate the control logic.
AV Rule 192 (MISRA Rule 60, Revised)
All if, else if constructs will contain either a final else clause or a comment indicating why a
final else clause is not necessary.
Rationale: Provide a defensive strategy to ensure that all cases are handled by an else if
series. See AV Rule 192 in Appendix A for examples.
Note: This rule only applies when an if statement is followed by one or more else if’s.

AV Rule 193 (MISRA Rule 61)
Every non-empty case clause in a switch statement shall be terminated with a break
statement.
Rationale: Eliminates potentially confusing behavior since execution will fall through to the
code of the next case clause if a break statement does not terminate the previous case clause.
See AV Rule 193 in Appendix A for an example.
AV Rule 194 (MISRA Rule 62, Revised)
All switch statements that do not intend to test for every enumeration value shall contain a
final default clause.
Rationale: Omitting the final default clause allows the compiler to provide a warning if all
enumeration values are not tested in a switch statement. Moreover, the lack of a default
clause indicates that a test for every case should be conducted. On the other hand, if all cases
are not tested for, then a final default clause must be included to handle those untested cases.
MISRA revised with shall replacing should.
AV Rule 195 (MISRA Rule 63)
A switch expression will not represent a Boolean value.
Rationale: An if statement provides a more natural representation.
AV Rule 196 (MISRA Rule 64, Revised)
Every switch statement will have at least two cases and a potential default.
Rationale: An if statement provides a more natural representation.
AV Rule 197 (MISRA Rule 65)
Floating point variables shall not be used as loop counters.
Rationale: Subjects the loop counter to rounding and truncation errors.
AV Rule 198
The initialization expression in a for loop will perform no actions other than to initialize the
value of a single for loop parameter. Note that the initialization expression may invoke an
accessor that returns an initial element in a sequence:
for (Iter_type p = c.begin() ; p != c.end() ; ++p) // Good
{
…
}
Rationale: Readability.

AV Rule 199
The increment expression in a for loop will perform no action other than to change a single
loop parameter to the next value for the loop.
Rationale: Readability.
AV Rule 200
Null initialize or increment expressions in for loops will not be used; a while loop will be
used instead.
Rationale: A while loop provides a more natural representation.
AV Rule 201 (MISRA Rule 67, Revised)
Numeric variables being used within a for loop for iteration counting shall not be modified
in the body of the loop.
Rationale: Readability and maintainability.
MISRA Rule 67 was revised by changing should to shall.
4.25 Expressions
AV Rule 202 (MISRA Rule 50)
Floating point variables shall not be tested for exact equality or inequality.
Rationale: Since floating point numbers are subject to rounding and truncation errors, exact
equality may not be achieved, even when expected.
AV Rule 203 (MISRA Rule 51, Revised)
Evaluation of expressions shall not lead to overflow/underflow (unless required
algorithmically and then should be heavily documented).
Rationale: Expressions leading to overflow/underflow typically indicate overflow error
conditions. See also AV Rule 212.
AV Rule 204
A single operation with side-effects shall only be used in the following contexts:
1. by itself
2. the right-hand side of an assignment
3. a condition
4. the only argument expression with a side-effect in a function call
5. condition of a loop
6. switch condition
7. single part of a chained operation.
Rationale: Readability. See AV Rule 204 in Appendix A for examples.

AV Rule 204.1 (MISRA Rule 46)
The value of an expression shall be the same under any order of evaluation that the standard
permits.
Rationale: Except where noted, the order in which operators and subexpression are
evaluated, as well as the order in which side effects take place, is unspecified [10], 5(4). See
AV Rule 204.1 in Appendix_A for examples.
AV Rule 205
The volatile keyword shall not be used unless directly interfacing with hardware.
Rationale: The volatile keyword is a hint to the compiler that an object’s value may change
in ways not specified by the language (e.g. object representing a hardware register). Hence,
aggressive optimizations should be avoided. [2]
4.26 Memory Allocation
AV Rule 206 (MISRA Rule 118, Revised)
Allocation/deallocation from/to the free store (heap) shall not occur after initialization.
Note that the “placement” operator new(), although not technically dynamic memory, may
only be used in low-level memory management routines. See AV Rule 70.1 for object
lifetime issues associated with placement operator new().
Rationale: repeated allocation (new/malloc) and deallocation (delete/free) from the free
store/heap can result in free store/heap fragmentation and hence non-deterministic delays in
free store/heap access. See Alloc.doc for alternatives.
AV Rule 207
Unencapsulated global data will be avoided.
Rationale: Global data is dangerous since no access protection is provided with respect to
the data.
Note: If multiple clients require access to a single resource, that resource should be
wrapped in a class that manages access to that resource. For example, semantic
controls that prohibit unrestricted access may be provided (e.g. singletons and
input streams). See AV_Rule_207_Appendix_A for examples.
4.27 Fault Handling
AV Rule 208
C++ exceptions shall not be used (i.e. throw, catch and try shall not be used.)
Rationale: Tool support is not adequate at this time.

4.28 Portable Code
4.28.1 Data Abstraction
AV Rule 209 (MISRA Rule 13, Revised)
The basic types of int, short, long, float and double shall not be used, but specific-length
equivalents should be typedef’d accordingly for each compiler, and these type names used in
the code.
Rationale: Since the storage length of types can vary from compiler to compiler and
platform-to-platform, this rule ensures that code can be easily reconfigured for storage size
differences by simply changing definitions in one file. See AV Rule 209 in Appendix A for
additional details.
Exception: Basic types are permitted in low-level routines to assist in the management of
word alignment issues (e.g. memory allocators).
MISRA rule was changed from should to shall.
4.28.2 Data Representation
AV Rule 210
Algorithms shall not make assumptions concerning how data is represented in memory (e.g.
big endian vs. little endian, base class subobject ordering in derived classes, nonstatic data
member ordering across access specifiers, etc.)
Rationale: Assumptions concerning architecture-specific aspects are non-portable.
Exception: Low level routines that are expressly written for the purpose of data formatting
(e.g. marshalling data, endian conversions, etc.) are permitted.
AV Rule 210.1
Algorithms shall not make assumptions concerning the order of allocation of nonstatic data
members separated by an access specifier. See also AV Rule 210 on data representation.
Rationale: The order of allocation of nonstatic data members, separated by an access-
specifier, is unspecified [10], 9.2(12). See AV Rule 210.1 in Appendix_A for additional
details.
AV Rule 211
Algorithms shall not assume that shorts, ints, longs, floats, doubles or long doubles begin at
particular addresses.
Rationale: The representation of data types in memory is highly machine-dependent. By
allocating data members to certain addresses, a processor may execute code more efficiently.
Because of this, the data structure that represents a structure or class will sometimes include
holes and be stored differently in different process architectures. Code which depends on a
specific representation is, of course, not portable.
Exception: Low level routines that are expressly written for the purpose of data formatting
(e.g. marshalling data, endian conversions, etc.) are permitted.

4.28.3 Underflow/Overflow
AV Rule 212
Underflow or overflow functioning shall not be depended on in any special way.
Rationale: Dependence on undefined language aspects leads to non-portable
implementations. See also AV Rule 203.
4.28.4 Order of Execution
AV Rule 213 (MISRA Rule 47, Revised)
No dependence shall be placed on C++’s operator precedence rules, below arithmetic
operators, in expressions.
Rationale: Readability. See AV Rule 213 in Appendix A for additional details.
MISRA Rule 47 changed by replacing should with shall.
AV Rule 214
Assuming that non-local static objects, in separate translation units, are initialized in a special
order shall not be done.
Rationale: Order dependencies lead to hard to find bugs. See AV Rule 214 in Appendix A
for additional details.
4.28.5 Pointer Arithmetic
AV Rule 215 (MISRA Rule 101)
Pointer arithmetic will not be used.
Rationale: The runtime computation of pointer values is error-prone (i.e. the computed value
may reference unintended or invalid memory locations). See AV Rule 97 and AV Rule 215
in Appendix A for additional information.
Exceptions: Objects such as containers, iterators, and allocators that manage pointer
arithmetic through well-defined interfaces are acceptable.

4.29 Efficiency Considerations
AV Rule 216
Programmers should not attempt to prematurely optimize code. See Meyers [7], item 16.
Rationale: Early focus on optimization can result in sacrificing the clarity and generality of
modules that will not be the true bottlenecks in the final system. See AV Rule 216 in
Appendix A for additional details.
Premature optimization is the root of all evil – Donald Knuth
Note: This rule does not preclude early consideration of fundamental algorithmic and data
structure efficiencies.
See also AV Rule 125 and AV Rule 177 for performance recommendations.
4.30 Miscellaneous
AV Rule 217
Compile-time and link-time errors should be preferred over run-time errors. See Meyers [6],
item 46.
Rationale: Errors detected at compile/link time will not occur at run time.
Whenever possible, push the detection of an error back from run-time to link-time, and
preferably compile-time. See also AV Rule 103 and AV Rule 194.
AV Rule 218
Compiler warning levels will be set in compliance with project policies.
Rationale: Compilers can typically be configured to generate a useful set of warning
messages that point out potential problems. Information gleaned from these messages could
be used to resolve certain errors before they occur at runtime.

5 TESTING
This section provides guidance when testing inheritance hierarchies that employ virtual
functions.
5.1.1 Subtypes
If D is a subtype of B, then instances of type D will function transparently in any context in
which instances of type B can exist. Thus it follows that all base class unit-level test cases must
be inherited by the test plan for derived classes. That is, derived classes must at least successfully
pass the test cases applicable to their base classes.3
AV Rule 219
All tests applied to a base class interface shall be applied to all derived class interfaces as
well. If the derived class poses stronger postconditions/invariants, then the new
postconditions /invariants shall be substituted in the derived class tests.
Rationale: A publicly-derived class must function transparently in the context of its base
classes.
Note: This rule will often imply that every test case appearing in the set of test cases
associated with a class will also appear in the set of test cases associated with each of
its derived classes.
5.1.2 Structure
AV Rule 220
Structural coverage algorithms shall be applied against flattened classes.
Rationale: Structural coverage reporting should be with respect to each class context—not a
summed across multiple class contexts. See AV Rule 220 in Appendix A for additional
details.
Note: When a class is viewed with respect to all of its components (both defined at the
derived level as well as inherited from all of its base levels) it is said to be flattened.
AV Rule 221
Structural coverage of a class within an inheritance hierarchy containing virtual functions
shall include testing every possible resolution for each set of identical polymorphic
references.
Rationale: Provide decision coverage for dispatch tables.
3 Note that subclass tests will often be extensions of the superclass tests.

