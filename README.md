# SIC-Assembler
A simple implementation of SIC assembler, written in python.


# Overview 
Simplified Instructional Computer (SIC) is a hypothetical computer that includes the
hardware features most often found on real machines. 

There are two versions of SIC,
1. SIC standard Model
2. SIC/XE (extra equipment or expensive)

In this repository, I implement the assembler of the former.

SIC instruction format : 
| Opcode : 8bits | x : 1bit | address : 15bits |
| ---| ---- | ---- |

demo picture : 

<pre>
                    input                                                       output(result)
</pre>

![image](https://user-images.githubusercontent.com/71260071/137664233-67934211-c964-4e86-b524-6075893e0cca.png)


# Requirements 
packages:
- numpy

# Usage 
1.Open git bash. 

2.Change the diretory where you want to do download this repository.
```
> cd (your directory)
```
3.Clone this repository. 
```
> git clone https://github.com/wei-0321/SIC-Assembler.git
```
4.Change the diretory to this repository.
```
> cd SIC-Assembler
```
5.Execute the program.
```
> python SIC.py
```


# Project Structure
```
(Path)                                	 (Description)
SIC-Assembler                            main folder     
│  │
│  ├ SIC.py                              main program
│  │
│  ├ input                               input directory
│  │  │
│  │  ├ example.txt                      the file you want to process
│  │
│  ├ output                              output directory
│  │  │
│  │  ├ example_result.txt               output result
│  │
