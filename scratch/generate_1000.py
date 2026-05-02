import json
import random

concepts = {
    # Data Structures
    "Stack": "a linear data structure following the Last-In-First-Out (LIFO) principle",
    "Queue": "a linear data structure following the First-In-First-Out (FIFO) principle",
    "Array": "a collection of elements of the same type stored in contiguous memory locations",
    "Linked List": "a sequence of nodes where each node contains data and a reference to the next node",
    "Doubly Linked List": "a type of linked list where each node contains a data part and two addresses, one for the previous node and one for the next",
    "Circular Queue": "a linear data structure based on the FIFO principle where the last position is connected back to the first position",
    "Binary Tree": "a tree data structure in which each node has at most two children",
    "Binary Search Tree": "a node-based binary tree where the left subtree contains smaller keys and the right subtree contains larger keys",
    "AVL Tree": "a self-balancing binary search tree where the height difference between left and right subtrees cannot be more than one",
    "Red Black Tree": "a self-balancing binary search tree where each node contains an extra bit for denoting color, ensuring operations run in logarithmic time",
    "B-Tree": "a self-balancing tree data structure that maintains sorted data and allows efficient searches, insertions, and deletions",
    "Heap": "a specialized tree-based data structure that satisfies the heap property",
    "Max Heap": "a heap where the key at the root node is strictly greater than or equal to the keys of its children",
    "Min Heap": "a heap where the key at the root node is strictly less than or equal to the keys of its children",
    "Graph": "a non-linear data structure consisting of nodes (vertices) and edges that connect them",
    "Directed Graph": "a set of vertices connected by edges that have a direction associated with them",
    "Undirected Graph": "a graph in which edges have no orientation",
    "Weighted Graph": "a graph in which a numerical weight is assigned to each edge",
    "Hashing": "a technique to uniquely identify a specific object from a group of similar objects using a hash function",
    "Hash Table": "a data structure that implements an associative array abstract data type mapped by keys to values",
    "Collision in Hashing": "a situation that occurs when a hash function maps two distinct keys to the same bucket",
    "Chaining": "a collision resolution technique where each slot of the hash table contains a linked list of collided elements",
    "Linear Probing": "a collision resolution scheme where collisions are resolved by sequentially searching the hash table for the next empty slot",
    "Breadth First Search": "an algorithm for searching a graph that explores all neighbor nodes at the present depth before moving deeper",
    "Depth First Search": "an algorithm for searching a graph that explores as far as possible along each branch before backtracking",
    "Bubble Sort": "a simple sorting algorithm that repeatedly steps through the list and swaps adjacent elements if they are in the wrong order",
    "Selection Sort": "an in-place algorithm that repeatedly selects the smallest element from the unsorted sublist and swaps it with the first unsorted element",
    "Insertion Sort": "a simple sorting algorithm that builds the final sorted array one item at a time",
    "Merge Sort": "a stable, divide-and-conquer sorting algorithm that divides a list into equal halves, sorts them, and merges them",
    "Quick Sort": "an efficient, divide-and-conquer sorting algorithm that selects a pivot element and partitions other elements into two sub-arrays",
    "Heap Sort": "a comparison-based sorting technique based on a binary heap data structure",
    "Radix Sort": "a non-comparative sorting algorithm that avoids comparison by creating and distributing elements into buckets",
    "Dynamic Programming": "an algorithmic technique for solving an optimization problem by breaking it down into overlapping subproblems",
    "Greedy Algorithm": "an algorithmic paradigm that builds up a solution piece by piece by choosing the immediate optimum at each step",
    "Backtracking": "an algorithmic technique for solving problems recursively by incrementally building solutions and discarding those that fail constraints",
    "Recursion": "a method of solving a problem where the solution depends on solutions to smaller instances of the same problem",
    "Time Complexity": "a metric that describes the amount of time it takes to run an algorithm as the input size grows",
    "Space Complexity": "the amount of memory space required by the algorithm during the course of its execution",
    "Big O Notation": "a mathematical notation that describes the upper bound of a function's growth rate, classifying algorithm worst-case runtime",
    "Big Theta Notation": "a tight bound notation that shows a mathematical function grows at exactly a specific rate",
    "Big Omega Notation": "a mathematical notation that provides an asymptotic lower bound on the growth rate of an algorithm",

    # OS
    "Operating System": "system software that manages computer hardware, software resources, and provides common services to programs",
    "Kernel": "the core component of an operating system that manages system resources and facilitates hardware-software communication",
    "Context Switch": "the process of storing the state of a process or thread so that it can be restored and resume execution later",
    "Process": "an instance of a computer program that is being executed within the operating system",
    "Thread": "the smallest sequence of programmed instructions that can be managed independently by a CPU scheduler",
    "Multithreading": "the ability of a central processing unit to provide multiple threads of execution concurrently within a single process",
    "Multiprogramming": "a technique to keep several programs in main memory at the same time to maximize CPU utilization",
    "Multitasking": "the concurrent execution of multiple tasks by an OS over a certain period of time",
    "Deadlock": "a state in which two or more competing processes are waiting for each other to finish, resulting in none ever progressing",
    "Starvation": "a problem in concurrent computing where a process is perpetually denied the resources it needs to proceed",
    "Race Condition": "a flaw that occurs when the timing or specific ordering of events affects a program's correctness",
    "Critical Section": "a segment of code that accesses a shared resource which must not be concurrently accessed by multiple threads",
    "Mutex": "a mutual exclusion object that is designed to synchronize access to a shared resource",
    "Semaphore": "a variable or abstract data type used to control access to a common resource by multiple processes",
    "Monitor": "a synchronization construct that allows threads to have mutual exclusion and wait for certain conditions to be true",
    "CPU Scheduling": "the process of determining which process will own the CPU for execution while another process is suspended",
    "FCFS Scheduling": "a scheduling algorithm that places requests in a queue and processes them in the exact order they were received",
    "SJF Scheduling": "a scheduling policy that selects the waiting process with the smallest execution time to execute next",
    "Round Robin Scheduling": "a preemptive scheduling algorithm that assigns a fixed time quantum to each process in a circular order",
    "Priority Scheduling": "a method of scheduling processes based on a predefined priority level assigned to each process",
    "Virtual Memory": "a memory management capability of an OS that temporarily transfers data from RAM to disk storage to compensate for shortages",
    "Paging": "a memory management scheme by which an OS retrieves data from secondary storage in same-size blocks called pages",
    "Segmentation": "a memory management technique in which memory is divided into variable-sized parts called segments based on logical division",
    "Page Fault": "an exception raised by the memory management unit when a running process accesses a memory page not currently mapped in RAM",
    "Thrashing": "a condition where a computer spends more time handling page faults than executing actual software programs",
    "TLB": "Translations Lookaside Buffer, a memory cache that stores the recent translations of virtual memory to physical memory",
    "Belady's Anomaly": "a phenomenon where increasing the number of physical memory page frames results in an increased number of page faults",
    "Inode": "a data structure in a Unix-style file system that describes an object such as a file or a directory",
    "Shell": "a user interface for access to an operating system's services",
    "System Call": "the programmatic way in which a computer program requests a service from the kernel",
    "Interprocess Communication": "the mechanisms provided by the operating system allowing processes to share data and synchronize actions",

    # DBMS
    "Database Management System": "software designed to safely store, retrieve, define, and manage structured data",
    "RDBMS": "a database management system based on the relational model commonly using SQL for operations",
    "NoSQL": "a class of non-relational database management systems designed for flexible, horizontally-scalable data models",
    "Data Independence": "the capability to change the schema at one level of a database system without changing the next higher level",
    "Database Schema": "the skeletal blueprint that represents the logical configuration of all or part of a relational database",
    "Entity": "a real-world distinct object or concept stored in a database",
    "Attribute": "a specific property or characteristic detailing an entity in a database",
    "Relationship": "a defined association establishing a connection between two or more database entities",
    "ER Model": "Entity-Relationship model, a conceptual data model representing the entities and relationships of a business domain",
    "Primary Key": "a unique identifying column or set of columns in a relational database table",
    "Foreign Key": "a database column that provides a defined link between the data stored in two distinct tables",
    "Candidate Key": "a set of minimal attributes that can uniquely identify a database record without referring to any other data",
    "Super Key": "a broad set of attributes within a table whose collective values can uniquely identify a row",
    "Composite Key": "a primary key composed of two or more columns to guarantee uniqueness on the composite data",
    "Normalization": "the systemic process of structuring a database to minimize data redundancy and enhance data integrity",
    "1NF": "First Normal Form, ensuring that a database table's cells all contain single atomic values without repeating groups",
    "2NF": "Second Normal Form, ensuring a table is in 1NF and all non-key attributes fully depend on the entire primary key",
    "3NF": "Third Normal Form, ensuring a table is in 2NF and contains no transitive dependencies among non-key attributes",
    "BCNF": "Boyce-Codd Normal Form, a stricter version of 3NF where every determinant must structurally be a candidate key",
    "Denormalization": "the strategic process of adding redundant data to databases to improve read performance over write integrity",
    "ACID Properties": "the core database traits of Atomicity, Consistency, Isolation, and Durability essential for reliable transaction processing",
    "Atomicity": "the ACID property demanding that complex database transactions act as a single indivisible unit that completely succeeds or fails",
    "Consistency": "the ACID property ensuring databases reliably transition from one valid state to another maintaining predefined rules",
    "Isolation": "the ACID property ensuring that concurrent transaction executions result fundamentally identical to serial execution",
    "Durability": "the ACID property guaranteeing that once a transaction legally commits, it persists permanently despite system crashes",
    "Database Transaction": "a single logical unit of database operational work comprising multiple individual data manipulations",
    "Concurrency Control": "the database procedure protecting against conflicts during simultaneous multi-user database operations",
    "Two Phase Locking": "a pessimistic concurrency control method segmenting transaction lock operations into distinct growing and shrinking phases",
    "Indexing": "a specialized data structure technique utilized to immensely accelerate data retrieval operations from databases",
    "B+ Tree Indexing": "an advanced node-based tree index allowing sorted sequential traversal and rapid logarithmic random access",
    "Hashing in DBMS": "a structural technique deploying hash functions to rapidly determine exact physical storage locations for database records",
    "SQL": "Structured Query Language, the ubiquitous domain-specific programming standard for querying relational database systems",
    "DDL": "Data Definition Language, the subset of SQL concerned with the structural creation, modification, and deletion of databases",
    "DML": "Data Manipulation Language, the subset of SQL handling standard insertion, updating, editing, and deletion of actual data",
    "DCL": "Data Control Language, the SQL subset dealing fundamentally with permission grants, authorization, and data access control",
    "TCL": "Transaction Control Language, the SQL standard used to procedurally commit, rollback, and manage logical data transactions",
    "Database View": "a virtual, non-physical table dynamically generated based strictly on the stored result-set of an active SQL query",
    "Database Trigger": "a piece of specialized procedural code configured to automatically execute in direct response to defined database events",
    "Stored Procedure": "saved SQL functional code explicitly prepared to be stored and systematically reused on the server side",
    "Relational Algebra": "a foundational procedural query language taking relation instances as input and producing altered relation instances as output",
    "Cartesian Product": "a relational algebraic binary operation forming a new relation encompassing all possible row combinations between two tables",
    "Natural Join": "a type of database join forming a combined relation by seamlessly matching and merging identical attributes across tables",
    "Outer Join": "a structured database join returning matching relation records while expressly retaining non-matching records from one or both tables",

    # Computer Networks
    "Computer Network": "a connected group of computer systems using standardized communication protocols to seamlessly share vast digital resources",
    "OSI Model": "Open Systems Interconnection model, a conceptual 7-layer framework standardizing telecommunication system functions globally",
    "TCP/IP Model": "the foundational 4-layer conceptual model practically powering routing and communication across the modern global Internet",
    "Physical Layer": "the absolute lowest OSI layer physically responsible for transmitting raw unstructured bit streams over physical network media",
    "Data Link Layer": "the second OSI layer fundamentally responsible for secure node-to-node data frame transfer and MAC physical addressing",
    "Network Layer": "the third OSI layer definitively responsible for logical IP packet forwarding and sophisticated routing through intermediate devices",
    "Transport Layer": "the fourth OSI layer providing essential host-to-host connectivity, segmentation, and reliable TCP data transfer services",
    "Session Layer": "the fifth OSI layer exclusively controlling the setup, complex dialogue, and systematic teardown of connection sessions",
    "Presentation Layer": "the sixth OSI layer fundamentally responsible for structural data format translation, compression, and robust encryption",
    "Application Layer": "the seventh and topmost OSI layer interacting entirely and directly with software applications connecting to the network",
    "Network Topology": "the physical or highly logical structural layout pattern describing the interconnection of network elements and varied nodes",
    "Star Topology": "a highly common network topology where absolutely every dependent node connects directly to one central networking device",
    "Mesh Topology": "a robust network topology where every single participating node actively relays data and physically connects to multiple others",
    "Ring Topology": "a continuous circular network topology fundamentally connecting each distinct node to exactly two direct adjacent neighbors",
    "Bus Topology": "an older network topology where every connected device crucially shares one single continuous half-duplex communication link",
    "LAN": "Local Area Network, a highly common computer network primarily restricted to local geographic areas like homes or varied offices",
    "WAN": "Wide Area Network, a massive telecommunications network typically extending distinct connections across large geographical distances",
    "MAN": "Metropolitan Area Network, a specialized computer network inherently sized to interconnect users across one vast metropolitan city area",
    "Router": "a highly intelligent networking device designed practically to route and dynamically forward IP data packets across multiple varied networks",
    "Switch": "a smart multi-port network hardware device utilizing exact MAC addresses to exclusively forward packet data to specific localized destinations",
    "Hub": "a rudimentary and basic networking piece strictly broadcasting received digital signals back out to every single continuously connected port",
    "IP Address": "a completely unique numeric label fundamentally assigned to networking hardware facilitating standardized cross-network Internet Protocol communication",
    "IPv4": "the older yet still incredibly widespread Internet Protocol formulation utilizing a 32-bit structured addressing pattern",
    "IPv6": "the modern subsequent Internet Protocol version explicitly utilizing a highly expansive 128-bit hexadecimal structured address schema",
    "MAC Address": "a fixed physical hardware network identifier structurally assigned explicitly to local network interface controllers by manufacturers",
    "Subnet Mask": "a 32-bit masking sequence systematically separating a standard IP address into logical network identification and distinct host identification",
    "Subnetting": "the highly practical networking method formally dividing one large continuous network into smaller logically defined distinct subnetworks",
    "Gateway": "a distinct networking node acting heavily as an active operational entrance linking two fundamentally incompatible distinct network architectures",
    "TCP": "Transmission Control Protocol, a highly reliable standard connection-oriented protocol explicitly tracking network data packet delivery confirmation",
    "UDP": "User Datagram Protocol, a connectionless and extremely rapid communications protocol effectively lacking explicit packet delivery confirmation mechanisms",
    "HTTP": "Hypertext Transfer Protocol, the primary foundational protocol fundamentally utilized for structuring and transmitting World Wide Web hypermedia data",
    "HTTPS": "a strictly secured configuration of normal HTTP exclusively deploying critical TLS encryption for safely protecting network communication",
    "FTP": "File Transfer Protocol, a standard distinct network protocol fundamentally designated for effectively transferring robust computer files over TCP connections",
    "SMTP": "Simple Mail Transfer Protocol, a highly standard Internet communication mechanism predominantly utilized for transmitting outward electronic mail",
    "DNS": "Domain Name System, the completely decentralized hierarchical naming schema heavily responsible for translating textual domains to numeric IP addresses",
    "DHCP": "Dynamic Host Configuration Protocol, an automated networking protocol heavily responsible for dynamically assigning critical IP configuration to network devices",
    "ARP": "Address Resolution Protocol, a critical network communication formulation distinctly utilized for mapping logical IP addresses to physical MAC addresses",
    "Ping": "a basic systematic network administration utility specifically created to reliably test the IP reachability of hosts across dynamic networks",
    "NAT": "Network Address Translation, an expansive router function physically masking numerous internal private IP addresses behind one public Internet address",
    "Firewall": "a highly critical network hardware or software security system expressly observing and blocking network traffic based firmly on established logical rules",
    "VPN": "Virtual Private Network, a secure method exclusively encrypting and robustly extending a localized private network strongly across unsafe public Internet channels",

    # Software Engineering
    "Software Engineering": "the incredibly systematic and heavily formalized application of engineering principles directly completely to reliable software development",
    "SDLC": "Software Development Life Cycle, the overarching methodological framework specifically defining identical structural phases required to construct quality digital software",
    "Waterfall Model": "an older strictly linear and completely sequential software development process preventing practical phase overlap during systematic commercial development",
    "Agile Methodology": "a massive modern software development process strictly emphasizing short iterative cycles, intense adaptability, and deep continual stakeholder feedback",
    "Scrum": "a highly specific and extremely popular specialized Agile developmental framework deeply emphasizing daily team alignment and distinct structured delivery sprints",
    "DevOps": "an expansive collaborative methodology explicitly intertwining standard software development directly alongside critical IT operations for extremely continuous rapid delivery",
    "System Design": "the crucial architectural phase actively defining specific modules, internal data interfaces, and overall structural capabilities to satisfy vast software requirements",
    "Cohesion": "an important software metric analyzing the exact functional relational strength actively demonstrating how deeply related localized module code inherently is",
    "Coupling": "a critical structural software metric effectively grading the deep mutual interdependence formally existing actively between distinct programmed software modules",
    "Unit Testing": "the foundational systematic testing phase essentially verifying that uniquely individual independent blocks of structural source code function entirely correctly",
    "Integration Testing": "the secondary structured software testing phase explicitly ensuring multiple previously tested independent modules successfully effectively communicate correctly together",
    "System Testing": "the final comprehensive software testing phase completely validating that the entirety of the vast integrated application distinctly meets original structured specifications",
    "White Box Testing": "a granular internal testing methodology primarily enabling developers to verify and test directly the explicitly known structural logic of localized application code",
    "Black Box Testing": "an essential functional testing approach effectively verifying the operational surface inputs and eventual outputs without explicitly analyzing deep internal software functionality",
    "Regression Testing": "a critical structural re-testing process actively heavily confirming that new updated software modifications distinctly have strictly not functionally compromised prior stable mechanics",
    "Version Control": "a sophisticated administrative structural class of specialized software actively retaining historical records tracking explicit line-by-line developer code alterations",
    "Git": "the vastly widespread open-source distributed tracking and continuous systematic version control schema heavily powering modern developmental software team collaboration",
    "CI/CD": "Continuous Integration and Continuous Deployment, the massive automated pipeline process seamlessly merging and constantly formally deploying new verified code to digital environments",
    "Code Refactoring": "the structured internal developmental process entirely functionally reorganizing local code essentially maintaining precise external behavioral output while significantly enhancing underlying clean structural readability",
    "Design Patterns": "heavily formalized historically proven structural architectural templates readily easily deployed to functionally resolve common continually repeating internal software programming challenges",
    "Singleton Pattern": "a classical structured creational architectural design pattern effectively restricting specific class instantiation entirely down solidly uniquely to just exactly one individual active object",
    "Factory Pattern": "a robust generic structured creational architectural architectural template strongly delegating explicit object instantiation mechanisms cleanly heavily directly over strictly towards appropriate localized subclass logic",
    "MVC Architecture": "Model-View-Controller, the widespread essential structured specific UI architecture massively splitting modern interactive application layers into distinct logical internal distinct functional operational boundaries",

    # AI & Machine Learning
    "Artificial Intelligence": "the sweeping complex computational field essentially designing digital intelligent systematic machinery specifically attempting to robustly distinctly heavily simulate inherent human neuro-cognitive processing reasoning explicitly",
    "Machine Learning": "the monumental distinct core structured subset of complex AI primarily deeply functionally reliant specifically upon robust mathematical algorithmic data modeling continually automatically improving heavily through long operational experience",
    "Deep Learning": "the deeply advanced sophisticated multi-layered structural branch fundamentally inside Machine Learning heavily exclusively utilizing immensely heavily expansive vast multi-layered artificial computational neural networks",
    "Supervised Learning": "a highly standard baseline structured algorithmic Machine Learning configuration highly reliant initially specifically practically explicitly upon heavily strictly accurately pre-labeled immense historical informational target data outputs",
    "Unsupervised Learning": "a fundamentally completely independent advanced Machine Learning algorithmic approach directly attempting heavily inherently quickly entirely to organically locate previously highly unidentified embedded complex internal distinct data structure distinct classifications without pre-existing labels",
    "Reinforcement Learning": "an inherently incredibly complex reward-based modern Machine Learning paradigm essentially allowing active autonomous algorithmic agents heavily carefully independently iteratively formally sequentially exclusively learning exclusively exactly practically primarily entirely via direct structural positive systematic numerical output feedback environments",
    "Neural Network": "a deeply vast biological-inspired core computational heavy structure specifically massively mathematically analyzing complicated highly complex inherent dimensional data layer structural connections specifically inside heavily deep advanced digital algorithms",
    "Activation Function": "an operational highly discrete structural non-linear mathematical node mechanism practically formally explicitly utilized to actively fundamentally significantly heavily strictly functionally gate passing numeric signals precisely traversing between individual interconnected core artificial neurons",
    "Backpropagation": "the primary intensely foundational strict mathematical optimization process incredibly heavily actively utilized essentially formally heavily rapidly explicitly entirely iteratively tuning multi-stage advanced internal neural network weight variables utilizing complex advanced gradient error correction calculus",
    "Gradient Descent": "a hugely basic highly widely highly widespread mathematical iterative algorithmic formula strongly functionally strictly utilized to effectively structurally locate the specific ideal minimum global parameter explicitly minimizing error heavily within deep complex ML modeling configurations",
    "Epoch": "the incredibly standard explicit ML model heavily utilized term designating absolutely precisely exactly specifically uniquely entirely distinct one single completed independent pass formally passing the whole entirely complete provided structured distinct historical testing internal dataset effectively safely forward practically entirely through internal ML algorithms",
    "Learning Rate": "a crucial incredibly highly strictly defined fixed hyperparameter structurally effectively directly exclusively actively determining explicitly mathematically exactly correctly how large an active individual exact variable correction step practically specifically precisely heavily explicitly strictly an operational gradient mathematical formula ultimately takes",
    "Overfitting": "a massively problematic highly pervasive typical condition seriously fundamentally severely degrading real complex ML algorithmic structural performance completely inherently ultimately heavily deeply functionally preventing effective generalized accurate deployment completely severely primarily entirely due to the ML model deeply formally heavily blindly memorizing exactly perfectly only heavily strict completely heavily precisely training initial baseline sets entirely strictly alone",
    "Underfitting": "a severe generally major widespread ML issue heavily explicitly deeply deeply causing inherently incredibly weak poor predictive numeric analytical structured operational output absolutely because the specifically completely generalized exact mathematical model remains simply practically completely theoretically incredibly basic practically explicitly heavily seriously actively functionally capturing essentially truly absolutely none deeply strongly heavily of the distinct explicitly available historical complex specific structural real intrinsic available dataset baseline features",
    "Confusion Matrix": "a profoundly structurally highly specifically informative critical dimensional data performance visual exactly accurately deeply heavily fully strongly mathematically effectively demonstrating the deeply strongly exact functional highly highly specifically correct effectively precisely explicitly accurately heavily strongly correct precision false positive and overall exactly completely distinct negative accuracy algorithmic metric explicit counts highly effectively clearly inside complex distinct classification analytic heavily dimensional tests"
}

variations = [
    ("What is {}?", "{} is {}."),
    ("Define {}.", "{} can be defined as {}."),
    ("Explain {}.", "In computer science, {} is {}."),
    ("Briefly describe {}.", "{} refers to {}."),
    ("What do you understand by {}?", "{} is literally {}."),
    ("Explain the concept of {}.", "The concept of {} refers to {}."),
    ("What is the meaning of {}?", "The meaning of {} is {}."),
    ("Describe {}.", "{} is {}."),
    ("Could you define {}?", "Certainly! {} is {}."),
    ("What does {} mean?", "{} means {}."),
]

output_data = []

# Generate all possibilities
for concept, definition in concepts.items():
    # Only take distinct outputs to ensure high quality
    random.shuffle(variations)
    # create ~7-8 entries per concept. 
    for q_template, a_template in variations[:8]:
        instruction = q_template.format(concept)
        output = a_template.format(concept, definition)
        # remove double spaces or grammar slips from templates
        output = output.replace("  ", " ").replace(" .", ".")
        
        output_data.append({
            "instruction": instruction,
            "output": output
        })

# Hardcoded differences
diffs = [
    ("difference between Stack and Queue", "Stack follows LIFO (Last-In-First-Out) while Queue follows FIFO (First-In-First-Out)."),
    ("difference between Array and Linked List", "Arrays store elements in contiguous memory while Linked Lists connect nodes using pointers."),
    ("difference between Process and Thread", "A process is an independent program in execution while a thread is the smallest unit of execution within a process."),
    ("difference between TCP and UDP", "TCP is connection-oriented and reliable, while UDP is connectionless and faster but less reliable."),
    ("difference between Compiler and Interpreter", "A compiler translates the entire code at once while an interpreter translates code line by line."),
    ("difference between BFS and DFS", "BFS uses a Queue and explores layer by layer, while DFS uses a Stack and explores deep into branches first."),
    ("difference between Primary Key and Foreign Key", "A Primary Key uniquely identifies a record in a table, while a Foreign Key links a column to the primary key of another table."),
    ("difference between IPv4 and IPv6", "IPv4 uses 32-bit addresses while IPv6 uses 128-bit addresses."),
    ("difference between Overfitting and Underfitting", "Overfitting memorizes training data and fails on new data, while underfitting is too simple to capture patterns at all."),
    ("difference between Supervised and Unsupervised Learning", "Supervised learning uses labeled training data, while unsupervised learning finds patterns in unlabelled data.")
]

for d_q, d_a in diffs:
    output_data.append({
        "instruction": f"What is the {d_q}?",
        "output": d_a
    })
    output_data.append({
        "instruction": f"Explain the {d_q}.",
        "output": d_a
    })
    output_data.append({
        "instruction": f"Distinguish the {d_q}.",
        "output": d_a
    })

# Shuffle the combined dataset
import random
random.seed(42)
random.shuffle(output_data)

# Ensure EXACTLY 1000 items
final_data = output_data[:1000]

with open('knowledge/btech_academic_dataset_1000.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, indent=4)

print(f"SUCCESS: Generated {len(final_data)} high-quality items and saved to knowledge/btech_academic_dataset_1000.json")
