While working on a syntactic analysis of expletive *there* in English, I encountered a great deal of discourse on which verbs could occur in such constructions. While there are certainly merits to this line of discussion --- it helps us discern what's going on under the hood of these constructions --- I am also concerned with which verbs **actually** occur in *there*-constructions in English. 

To this end, I extracted sentences containing expletive *there* from the FrameNet corpus. That is, I selected sentences which contained an element with the PoS tag EX or ex0, and extracted the last verb in their clause. I hand-removed examples in which referential *there* had been misannotated as expletive *there*, like in (1), and examples where the verb was misidentified because of syntactic weirdnesses, like in (2). These were easily identifiable, because their purported verbs were conspicuously implausible. These examples have been collected in `false_positives.json`.

1. Sentence 1412513: "From there he was transferred to a prison in Rabat , where he was severely tortured for the next three days ."
	The verb here is supposedly "he".

2. Sentence 1323425: "There seems to be no technical problem in taking the switchboard away from reception and Tony Frost is researching where else it could be sited ."
	The verb detected here is *seem*, but it is actually *be*. This is a common error with what are known as "control verbs".


After this process, I ended up with 6021 instances of true expletive *there*. all but 52 had some form of *be* as their main verb. These are the non-*be* verbs that truly appeared in *there*-structures:

| Verb    | \# of Occurrences | 
| ------- | ----------------- |
| follow  | 17                |
| seem    | 8                 |
| come    | 7                 |
| remain  | 6                 |
| exist   | 6                 |
| peep    | 1                 |
| grow up | 1                 |
| emerge  | 1                 |
| fall    | 1                 |
| look    | 1                 |
| lurk    | 1                 |
| stretch | 1                 |
| lie     | 1                 |