# AV Rule Index

Quick-reference index of all 228 AV Rules (rule number, MISRA cross-reference, one-line summary). This is for locating the right rule fast. For full rule text, rationale, and exceptions, read the relevant section of standards-body.md. For code examples, see appendix-a-examples.md (organized by rule number).

| Rule | MISRA Ref | Summary |
|---|---|---|
| AV Rule 1 |  | Any one function (or method) will contain no more than 200 logical source lines of code (L- SLOCs). |
| AV Rule 2 |  | There shall not be any self-modifying code. |
| AV Rule 3 |  | All functions shall have a cyclomatic complexity number of 20 or less. |
| AV Rule 4 |  | To break a “should” rule, the following approval must be received by the developer: • approval from the software engineering lead (obtained by the unit approval in the de |
| AV Rule 5 |  | To break a “will” or a “shall” rule, the following approvals must be received by the developer: • approval from the software engineering lead (obtained by the unit approv |
| AV Rule 6 |  | Each deviation from a “shall” rule shall be documented in the file that contains the deviation). Deviations from this rule shall not be allowed, AV Rule 5 notwithstanding |
| AV Rule 7 |  | Approval will not be required for a deviation from a “shall” or “will” rule that complies with an exception specified by that rule. |
| AV Rule 8 |  | All code shall conform to ISO/IEC 14882:2002(E) standard C++. [10] |
| AV Rule 9 | (MISRA Rule 5, Revised) | Only those characters specified in the C++ basic source character set will be used. This set includes 96 characters: the space character, the control characters represent |
| AV Rule 10 | (MISRA Rule 6) | Values of character types will be restricted to a defined and documented subset of ISO 10646-1. [9] |
| AV Rule 11 | (MISRA Rule 7) | Trigraphs will not be used. Trigraph sequences are three-character sequences that are replaced by a corresponding single character, as follows: Alternative Primary altern |
| AV Rule 13 | (MISRA Rule 8) | Multi-byte characters and wide string literals will not be used. |
| AV Rule 14 |  | Literal suffixes shall use uppercase rather than lowercase letters. |
| AV Rule 15 | (MISRA Rule 4, Revised) | Provision shall be made for run-time checking (defensive programming). |
| AV Rule 16 |  | Only DO-178B level A [15] certifiable or SEAL 1 C/C++ libraries shall be used with safety- critical (i.e. SEAL 1) code [13]. |
| AV Rule 17 | (MISRA Rule 119) | The error indicator errno shall not be used. Exception: If there is no other reasonable way to communicate an error condition to an application, then errno may be used. F |
| AV Rule 18 | (MISRA Rule 120) | The macro offsetof, in library <stddef.h>, shall not be used. |
| AV Rule 19 | (MISRA Rule 121) | <locale.h> and the setlocale function shall not be used. |
| AV Rule 20 | (MISRA Rule 122) | The setjmp macro and the longjmp function shall not be used. |
| AV Rule 21 | (MISRA Rule 123) | The signal handling facilities of <signal.h> shall not be used. |
| AV Rule 22 | (MISRA Rule 124, Revised) | The input/output library <stdio.h> shall not be used. |
| AV Rule 23 | (MISRA Rule 125) | The library functions atof, atoi and atol from library <stdlib.h> shall not be used. Exception: If required, atof, atoi and atol may be used only after design and impleme |
| AV Rule 24 | (MISRA Rule 126) | The library functions abort, exit, getenv and system from library <stdlib.h> shall not be used. |
| AV Rule 25 | (MISRA Rule 127) | The time handling functions of library <time.h> shall not be used. |
| AV Rule 26 |  | Only the following pre-processor directives shall be used: 1. #ifndef 2. #define 3. #endif 4. #include |
| AV Rule 27 |  | #ifndef, #define and #endif will be used to prevent multiple inclusions of the same header file. Other techniques to prevent the multiple inclusions of header files will  |
| AV Rule 28 |  | The #ifndef and #endif pre-processor directives will only be used as defined in AV Rule 27 to prevent multiple inclusions of the same header file. |
| AV Rule 29 |  | The #define pre-processor directive shall not be used to create inline macros. Inline functions shall be used instead. |
| AV Rule 30 |  | The #define pre-processor directive shall not be used to define constant values. Instead, the const qualifier shall be applied to variable declarations to specify constan |
| AV Rule 31 |  | The #define pre-processor directive will only be used as part of the technique to prevent multiple inclusions of the same header file. |
| AV Rule 32 |  | The #include pre-processor directive will only be used to include header (*.h) files. Exception: In the case of template class or function definitions, the code may be pa |
| AV Rule 33 |  | The #include directive shall use the <filename.h> notation to include header files. Note that relative pathnames may also be used. See also AV Rule 53, AV Rule 53.1, and  |
| AV Rule 34 |  | Header files should contain logically related declarations only. |
| AV Rule 35 |  | A header file will contain a mechanism that prevents multiple inclusions of itself. |
| AV Rule 36 |  | Compilation dependencies should be minimized when possible. (Stroustrup [2], Meyers [6], item 34) |
| AV Rule 37 |  | Header (include) files should include only those header files that are required for them to successfully compile. Files that are only used by the associated .cpp file sho |
| AV Rule 38 |  | Declarations of classes that are only accessed via pointers (*) or references (&) should be supplied by forward headers that contain only forward declarations. |
| AV Rule 39 |  | Header files (*.h) will not contain non-const variable definitions or function definitions. (See also AV Rule 139.) |
| AV Rule 40 |  | Every implementation file shall include the header files that uniquely define the inline functions, types, and templates used. |
| AV Rule 41 |  | Source lines will be kept to a length of 120 characters or less. |
| AV Rule 42 |  | Each expression-statement will be on a separate line. |
| AV Rule 43 |  | Tabs should be avoided. |
| AV Rule 44 |  | All indentations will be at least two spaces and be consistent within the same source file. |
| AV Rule 45 |  | All words in an identifier will be separated by the ‘_’ character. |
| AV Rule 46 | (MISRA Rule 11, Revised) | User-specified identifiers (internal and external) will not rely on significance of more than 64 characters. |
| AV Rule 47 |  | Identifiers will not begin with the underscore character ‘_’. |
| AV Rule 48 |  | Identifiers will not differ by: • Only a mixture of case • The presence/absence of the underscore character • The interchange of the letter ‘O’, with the number ‘0’ or th |
| AV Rule 49 |  | All acronyms in an identifier will be composed of uppercase letters. |
| AV Rule 50 |  | The first word of the name of a class, structure, namespace, enumeration, or type created with typedef will begin with an uppercase letter. All others letters will be low |
| AV Rule 51 |  | All letters contained in function and variable names will be composed entirely of lowercase letters. |
| AV Rule 52 |  | Identifiers for constant and enumerator values shall be lowercase. Example: const uint16 max_pressure = 100; enum Switch_position {up, down}; |
| AV Rule 53 |  | Header files will always have a file name extension of ".h". |
| AV Rule 53.1 |  | The following character sequences shall not appear in header file names: ‘, \, /*, //, or ". |
| AV Rule 54 |  | Implementation files will always have a file name extension of ".cpp". |
| AV Rule 55 |  | The name of a header file should reflect the logical entity for which it provides declarations. Example: For the Matrix entity, the header file would be named: Matrix.h |
| AV Rule 56 |  | The name of an implementation file should reflect the logical entity for which it provides definitions and have a “.cpp” extension (this name will normally be identical t |
| AV Rule 57 |  | The public, protected, and private sections of a class will be declared in that order (the public section is declared before the protected section which is declared befor |
| AV Rule 58 |  | When declaring and defining functions with more than two parameters, the leading parenthesis and the first argument will be written on the same line as the function name. |
| AV Rule 59 | (MISRA Rule 59, Revised) | The statements forming the body of an if, else if, else, while, do…while or for statement shall always be enclosed in braces, even if the braces form an empty block. |
| AV Rule 60 |  | Braces ("{}") which enclose a block will be placed in the same column, on separate lines directly before and after the block. Example: if (var_name == true) { } else { } |
| AV Rule 61 |  | Braces ("{}") which enclose a block will have nothing else on the line except comments (if necessary). |
| AV Rule 62 |  | The dereference operator ‘*’ and the address-of operator ‘&’ will be directly connected with the type-specifier. |
| AV Rule 63 |  | Spaces will not be used around ‘.’ or ‘->’, nor between unary operators and operands. |
| AV Rule 64 |  | A class interface should be complete and minimal. See Meyers [6], item 18. |
| AV Rule 65 |  | A structure should be used to model an entity that does not require an invariant. |
| AV Rule 66 |  | A class should be used to model an entity that maintains an invariant. |
| AV Rule 67 |  | Public and protected data should only be used in structs—not classes. |
| AV Rule 68 |  | Unneeded implicitly generated member functions shall be explicitly disallowed. See Meyers [6], item 27. |
| AV Rule 69 |  | A member function that does not affect the state of an object (its instance variables) will be declared const. Member functions should be const by default. Only when ther |
| AV Rule 70 |  | A class will have friends only when a function or object requires access to the private elements of the class, but is unable to be a member of the class for logical or ef |
| AV Rule 70.1 |  | An object shall not be improperly used before its lifetime begins or after its lifetime ends. |
| AV Rule 71 |  | Calls to an externally visible operation of an object, other than its constructors, shall not be allowed until the object has been fully initialized. |
| AV Rule 71.1 |  | A class’s virtual functions shall not be invoked from its destructor or any of its constructors. |
| AV Rule 72 |  | The invariant2 for a class should be: • a part of the postcondition of every class constructor, • a part of the precondition of the class destructor (if any), • a part of |
| AV Rule 73 |  | Unnecessary default constructors shall not be defined. See Meyers [7], item 4. (See also AV Rule 143). |
| AV Rule 74 |  | Initialization of nonstatic class members will be performed through the member initialization list rather than through assignment in the body of a constructor. See Meyers |
| AV Rule 75 |  | Members of the initialization list shall be listed in the order in which they are declared in the class. See Stroustrup [2], 10.4.5 and Meyers [6], item 13. |
| AV Rule 76 |  | A copy constructor and an assignment operator shall be declared for classes that contain pointers to data items or nontrivial destructors. See Meyers [6], item 11. |
| AV Rule 77 |  | A copy constructor shall copy all data members and bases that affect the class invariant (a data element representing a cache, for example, would not need to be copied). |
| AV Rule 77.1 |  | The definition of a member function shall not contain default arguments that produce a signature identical to that of the implicitly-declared copy constructor for the cor |
| AV Rule 78 |  | All base classes with a virtual function shall define a virtual destructor. |
| AV Rule 79 |  | All resources acquired by a class shall be released by the class’s destructor. See Stroustrup [2], 14.4 and Meyers [7], item 9. |
| AV Rule 80 |  | The default copy and assignment operators will be used for classes when those operators offer reasonable semantics. |
| AV Rule 81 |  | The assignment operator shall handle self-assignment correctly (see Stroustrup [2], Appendix E.3.3 and 10.4.4) |
| AV Rule 82 |  | An assignment operator shall return a reference to *this. |
| AV Rule 83 |  | An assignment operator shall assign all data members and bases that affect the class invariant (a data element representing a cache, for example, would not need to be cop |
| AV Rule 84 |  | Operator overloading will be used sparingly and in a conventional manner. |
| AV Rule 85 |  | When two operators are opposites (such as == and !=), both will be defined and one will be defined in terms of the other. |
| AV Rule 86 |  | Concrete types should be used to represent simple independent concepts. See Stroustrup [2], 25.2. |
| AV Rule 87 |  | Hierarchies should be based on abstract classes. See Stroustrup [2], 12.5. |
| AV Rule 88 |  | Multiple inheritance shall only be allowed in the following restricted form: n interfaces plus m private implementations, plus at most one protected implementation. |
| AV Rule 88.1 |  | A stateful virtual base shall be explicitly declared in each derived class that accesses it. |
| AV Rule 89 |  | A base class shall not be both virtual and non-virtual in the same hierarchy. |
| AV Rule 90 |  | Heavily used interfaces should be minimal, general and abstract. See Stroustrup [2] 23.4. |
| AV Rule 91 |  | Public inheritance will be used to implement “is-a” relationships. See Meyers [6], item 35. |
| AV Rule 92 |  | A subtype (publicly derived classes) will conform to the following guidelines with respect to all classes involved in the polymorphic assignment of different subclass ins |
| AV Rule 93 |  | “has-a” or “is-implemented-in-terms-of” relationships will be modeled through membership or non-public inheritance. See Meyers [6], item 40. |
| AV Rule 94 |  | An inherited nonvirtual function shall not be redefined in a derived class. See Meyers [6], item 37. |
| AV Rule 95 |  | An inherited default parameter shall never be redefined. See Meyers [6], item 38. |
| AV Rule 96 |  | Arrays shall not be treated polymorphically. See Meyers [7], item 3. |
| AV Rule 97 |  | Arrays shall not be used in interfaces. Instead, the Array class should be used. |
| AV Rule 97.1 |  | Neither operand of an equality operator (== or !=) shall be a pointer to a virtual member function. |
| AV Rule 98 |  | Every nonlocal name, except main(), should be placed in some namespace. See Stroustrup [2], 8.2. |
| AV Rule 99 |  | Namespaces will not be nested more than two levels deep. |
| AV Rule 100 |  | Elements from a namespace should be selected as follows: • using declaration or explicit qualification for few (approximately five) names, • using directive for many name |
| AV Rule 101 |  | Templates shall be reviewed as follows: 1. with respect to the template in isolation considering assumptions or requirements placed on its arguments. 2. with respect to a |
| AV Rule 102 |  | Template tests shall be created to cover all actual template instantiations. |
| AV Rule 103 |  | Constraint checks should be applied to template arguments. |
| AV Rule 104 |  | A template specialization shall be declared before its use. See Stroustrup [2], 13.5. |
| AV Rule 105 |  | A template definition’s dependence on its instantiation contexts should be minimized. See Stroustrup [2], 13.2.5 and C.13.8. |
| AV Rule 106 |  | Specializations for pointer types should be made where appropriate. See Stroustrup [2], 13.5. |
| AV Rule 107 | (MISRA Rule 68) | Functions shall always be declared at file scope. |
| AV Rule 108 | (MISRA Rule 69) | Functions with variable numbers of arguments shall not be used. |
| AV Rule 109 |  | A function definition should not be placed in a class specification unless the function is intended to be inlined. |
| AV Rule 110 |  | Functions with more than 7 arguments will not be used. |
| AV Rule 111 |  | A function shall not return a pointer or reference to a non-static local object. |
| AV Rule 112 |  | Function return values should not obscure resource ownership. |
| AV Rule 113 | (MISRA Rule 82, Revised) | Functions will have a single exit point. |
| AV Rule 114 | (MISRA Rule 83, Revised) | All exit points of value-returning functions shall be through return statements. |
| AV Rule 115 | (MISRA Rule 86) | If a function returns error information, then that error information will be tested. |
| AV Rule 116 |  | Small, concrete-type arguments (two or three words in size) should be passed by value if changes made to formal parameters should not be reflected in the calling function |
| AV Rule 117 |  | Arguments should be passed by reference if NULL values are not possible: AV Rule 117.1 An object should be passed as const T& if the function should not change the value  |
| AV Rule 118 |  | Arguments should be passed via pointers if NULL values are possible: AV Rule 118.1 An object should be passed as const T* if its value should not be modified. AV Rule 118 |
| AV Rule 119 | (MISRA Rule 70) | Functions shall not call themselves, either directly or indirectly (i.e. recursion shall not be allowed). |
| AV Rule 120 |  | Overloaded operations or methods should form families that use the same semantics, share the same name, have the same purpose, and that are differentiated by formal param |
| AV Rule 121 |  | Only functions with 1 or 2 statements should be considered candidates for inline functions. |
| AV Rule 122 |  | Trivial accessor and mutator functions should be inlined. |
| AV Rule 123 |  | The number of accessor and mutator functions should be minimized. |
| AV Rule 124 |  | Trivial forwarding functions should be inlined. |
| AV Rule 125 |  | Unnecessary temporary objects should be avoided. See Meyers [7], item 19, 20, 21. |
| AV Rule 126 |  | Only valid C++ style comments (//) shall be used. See AV Rule 126 in Appendix A for additional details concerning valid C++ style comments. |
| AV Rule 127 |  | Code that is not used (commented out) shall be deleted. |
| AV Rule 128 |  | Comments that document actions or sources (e.g. tables, figures, paragraphs, etc.) outside of the file being documented will not be allowed. |
| AV Rule 129 |  | Comments in header files should describe the externally visible behavior of the functions or classes being documented. |
| AV Rule 130 |  | The purpose of every line of executable code should be explained by a comment, although one comment may describe more than one line of code. |
| AV Rule 131 |  | One should avoid stating in comments what is better stated in code (i.e. do not simply repeat what is in the code). |
| AV Rule 132 |  | Each variable declaration, typedef, enumeration value, and structure member will be commented. Exception: Cases where commenting would be unnecessarily redundant. |
| AV Rule 133 |  | Every source file will be documented with an introductory comment that provides information on the file name, its contents, and any program-required information (e.g. leg |
| AV Rule 134 |  | Assumptions (limitations) made by functions should be documented in the function’s preamble. |
| AV Rule 135 | (MISRA Rule 21, Revised) | Identifiers in an inner scope shall not use the same name as an identifier in an outer scope, and therefore hide that identifier. |
| AV Rule 136 | (MISRA Rule 22, Revised) | Declarations should be at the smallest feasible scope. (See also AV Rule 143). |
| AV Rule 137 | (MISRA Rule 23) | All declarations at file scope should be static where possible. |
| AV Rule 138 | (MISRA Rule 24) | Identifiers shall not simultaneously have both internal and external linkage in the same translation unit. |
| AV Rule 139 | (MISRA Rule 27) | External objects will not be declared in more than one file. (See also AV Rule 39.) |
| AV Rule 140 | (MISRA Rule 28, Revised) | The register storage class specifier shall not be used. |
| AV Rule 141 |  | A class, structure, or enumeration will not be declared in the definition of its type. |
| AV Rule 142 | (MISRA Rule 30, Revised) | All variables shall be initialized before use. (See also AV Rule 136, AV Rule 71, and AV Rule 73, and AV Rule 143 concerning declaration scope, object construction, defau |
| AV Rule 143 |  | Variables will not be introduced until they can be initialized with meaningful values. (See also AV Rule 136, AV Rule 142, and AV Rule 73 concerning declaration scope, in |
| AV Rule 144 | (MISRA Rule 31) | Braces shall be used to indicate and match the structure in the non-zero initialization of arrays and structures. |
| AV Rule 145 | (MISRA Rule 32 ) | In an enumerator list, the ‘=‘ construct shall not be used to explicitly initialize members other than the first, unless all items are explicitly initialized. |
| AV Rule 146 | (MISRA Rule 15) | Floating point implementations shall comply with a defined floating point standard. The standard that will be used is the ANSI/IEEE Std 754 [1]. |
| AV Rule 147 | (MISRA Rule 16) | The underlying bit representations of floating point numbers shall not be used in any way by the programmer. |
| AV Rule 148 |  | Enumeration types shall be used instead of integer types (and constants) to select from a limited series of choices. |
| AV Rule 149 | (MISRA Rule 19) | Octal constants (other than zero) shall not be used. |
| AV Rule 150 |  | Hexadecimal constants will be represented using all uppercase letters. |
| AV Rule 151 |  | Numeric values in code will not be used; symbolic values will be used instead. |
| AV Rule 151.1 |  | A string literal shall not be modified. Note that strictly conforming compilers should catch violations, but many do not. |
| AV Rule 152 |  | Multiple variable declarations shall not be allowed on the same line. |
| AV Rule 153 | (MISRA Rule 110, Revised) | Unions shall not be used. |
| AV Rule 154 | (MISRA Rules 111 and 112, Revised) | Bit-fields shall have explicitly unsigned integral or enumeration types only. |
| AV Rule 155 |  | Bit-fields will not be used to pack data into a word for the sole purpose of saving space. |
| AV Rule 156 | (MISRA Rule 113) | All the members of a structure (or class) shall be named and shall only be accessed via their names. |
| AV Rule 157 | (MISRA Rule 33) | The right hand operand of a && or || operator shall not contain side effects. |
| AV Rule 158 | (MISRA Rule 34) | The operands of a logical && or || shall be parenthesized if the operands contain binary operators. |
| AV Rule 159 |  | Operators ||, &&, and unary & shall not be overloaded. See Meyers [7], item 7. |
| AV Rule 160 | (MISRA Rule 35, Modified) | An assignment expression shall be used only as the expression in an expression statement. |
| AV Rule 162 |  | Signed and unsigned values shall not be mixed in arithmetic or comparison operations. |
| AV Rule 163 |  | Unsigned arithmetic shall not be used. |
| AV Rule 164 | (MISRA Rule 38) | The right hand operand of a shift operator shall lie between zero and one less than the width in bits of the left-hand operand (inclusive). |
| AV Rule 164.1 |  | The left-hand operand of a right-shift operator shall not have a negative value. |
| AV Rule 165 | (MISRA Rule 39) | The unary minus operator shall not be applied to an unsigned expression. |
| AV Rule 166 | (MISRA Rule 40) | The sizeof operator will not be used on expressions that contain side effects. |
| AV Rule 167 | (MISRA Rule 41) | The implementation of integer division in the chosen compiler shall be determined, documented and taken into account. |
| AV Rule 168 | (MISRA Rule 42, Revised) | The comma operator shall not be used. |
| AV Rule 169 |  | Pointers to pointers should be avoided when possible. |
| AV Rule 170 | (MISRA Rule 102, Revised) | More than 2 levels of pointer indirection shall not be used. |
| AV Rule 171 | (MISRA Rule 103) | Relational operators shall not be applied to pointer types except where both operands are of the same type and point to: • the same object, • the same function, • members |
| AV Rule 173 | (MISRA Rule 106, Revised) | The address of an object with automatic storage shall not be assigned to an object which persists after the object has ceased to exist. |
| AV Rule 174 | (MISRA Rule 107) | The null pointer shall not be de-referenced. |
| AV Rule 175 |  | A pointer shall not be compared to NULL or be assigned NULL; use plain 0 instead. |
| AV Rule 176 |  | A typedef will be used to simplify program syntax when declaring function pointers. |
| AV Rule 177 |  | User-defined conversion functions should be avoided. See Meyers [7], item 5. |
| AV Rule 178 |  | Down casting (casting from base to derived class) shall only be allowed through one of the following mechanism: • Virtual functions that act like dynamic casts (most like |
| AV Rule 179 |  | A pointer to a virtual base class shall not be converted to a pointer to a derived class. |
| AV Rule 180 | (MISRA Rule 43) | Implicit conversions that may result in a loss of information shall not be used. |
| AV Rule 181 | (MISRA Rule 44) | Redundant explicit casts will not be used. |
| AV Rule 182 | (MISRA Rule 45) | Type casting from any type to or from pointers shall not be used. |
| AV Rule 183 |  | Every possible measure should be taken to avoid type casting. |
| AV Rule 184 |  | Floating point numbers shall not be converted to integers unless such a conversion is a specified algorithmic requirement or is necessary for a hardware interface. |
| AV Rule 185 |  | C++ style casts (const_cast, reinterpret_cast, and static_cast) shall be used instead of the traditional C-style casts. See Stroustrup [2], 15.4 and Meyers [7], item 2. |
| AV Rule 186 | (MISRA Rule 52) | There shall be no unreachable code. |
| AV Rule 187 | (MISRA Rule 53, Revised) | All non-null statements shall potentially have a side-effect. |
| AV Rule 188 | (MISRA Rule 55, Revised) | Labels will not be used, except in switch statements. |
| AV Rule 189 | (MISRA Rule 56) | The goto statement shall not be used. |
| AV Rule 190 | (MISRA Rule 57) | The continue statement shall not be used. |
| AV Rule 191 | (MISRA Rule 58) | The break statement shall not be used (except to terminate the cases of a switch statement). Exception: The break statement may be used to “break” out of a single loop pr |
| AV Rule 192 | (MISRA Rule 60, Revised) | All if, else if constructs will contain either a final else clause or a comment indicating why a final else clause is not necessary. |
| AV Rule 193 | (MISRA Rule 61) | Every non-empty case clause in a switch statement shall be terminated with a break statement. |
| AV Rule 194 | (MISRA Rule 62, Revised) | All switch statements that do not intend to test for every enumeration value shall contain a final default clause. |
| AV Rule 195 | (MISRA Rule 63) | A switch expression will not represent a Boolean value. |
| AV Rule 196 | (MISRA Rule 64, Revised) | Every switch statement will have at least two cases and a potential default. |
| AV Rule 197 | (MISRA Rule 65) | Floating point variables shall not be used as loop counters. |
| AV Rule 198 |  | The initialization expression in a for loop will perform no actions other than to initialize the value of a single for loop parameter. Note that the initialization expres |
| AV Rule 199 |  | The increment expression in a for loop will perform no action other than to change a single loop parameter to the next value for the loop. |
| AV Rule 200 |  | Null initialize or increment expressions in for loops will not be used; a while loop will be used instead. |
| AV Rule 201 | (MISRA Rule 67, Revised) | Numeric variables being used within a for loop for iteration counting shall not be modified in the body of the loop. |
| AV Rule 202 | (MISRA Rule 50) | Floating point variables shall not be tested for exact equality or inequality. |
| AV Rule 203 | (MISRA Rule 51, Revised) | Evaluation of expressions shall not lead to overflow/underflow (unless required algorithmically and then should be heavily documented). |
| AV Rule 204 |  | A single operation with side-effects shall only be used in the following contexts: 1. by itself 2. the right-hand side of an assignment 3. a condition 4. the only argumen |
| AV Rule 204.1 | (MISRA Rule 46) | The value of an expression shall be the same under any order of evaluation that the standard permits. |
| AV Rule 205 |  | The volatile keyword shall not be used unless directly interfacing with hardware. |
| AV Rule 206 | (MISRA Rule 118, Revised) | Allocation/deallocation from/to the free store (heap) shall not occur after initialization. Note that the “placement” operator new(), although not technically dynamic mem |
| AV Rule 207 |  | Unencapsulated global data will be avoided. |
| AV Rule 208 |  | C++ exceptions shall not be used (i.e. throw, catch and try shall not be used.) |
| AV Rule 209 | (MISRA Rule 13, Revised) | The basic types of int, short, long, float and double shall not be used, but specific-length equivalents should be typedef’d accordingly for each compiler, and these type |
| AV Rule 210 |  | Algorithms shall not make assumptions concerning how data is represented in memory (e.g. big endian vs. little endian, base class subobject ordering in derived classes, n |
| AV Rule 210.1 |  | Algorithms shall not make assumptions concerning the order of allocation of nonstatic data members separated by an access specifier. See also AV Rule 210 on data represen |
| AV Rule 211 |  | Algorithms shall not assume that shorts, ints, longs, floats, doubles or long doubles begin at particular addresses. |
| AV Rule 212 |  | Underflow or overflow functioning shall not be depended on in any special way. |
| AV Rule 213 | (MISRA Rule 47, Revised) | No dependence shall be placed on C++’s operator precedence rules, below arithmetic operators, in expressions. |
| AV Rule 214 |  | Assuming that non-local static objects, in separate translation units, are initialized in a special order shall not be done. |
| AV Rule 215 | (MISRA Rule 101) | Pointer arithmetic will not be used. |
| AV Rule 216 |  | Programmers should not attempt to prematurely optimize code. See Meyers [7], item 16. |
| AV Rule 217 |  | Compile-time and link-time errors should be preferred over run-time errors. See Meyers [6], item 46. |
| AV Rule 218 |  | Compiler warning levels will be set in compliance with project policies. |
| AV Rule 219 |  | All tests applied to a base class interface shall be applied to all derived class interfaces as well. If the derived class poses stronger postconditions/invariants, then  |
| AV Rule 220 |  | Structural coverage algorithms shall be applied against flattened classes. |
| AV Rule 221 |  | Structural coverage of a class within an inheritance hierarchy containing virtual functions shall include testing every possible resolution for each set of identical poly |
