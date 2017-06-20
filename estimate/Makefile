SYSTEM     = x86-64_linux
LIBFORMAT  = static_pic

#------------------------------------------------------------
#
# When you adapt this makefile to compile your CPLEX programs
# please copy this makefile and set CPLEXDIR and CONCERTDIR to
# the directories where CPLEX and CONCERT are installed.
#
#------------------------------------------------------------

#CPLEXDIR      = ../../..
#CONCERTDIR    = ../../../../concert

CPLEXDIR      =  /opt/ibm/ILOG/CPLEX_Studio1271/cplex
CONCERTDIR    =  /opt/ibm/ILOG/CPLEX_Studio1271/concert

# ---------------------------------------------------------------------
# Compiler selection
# ---------------------------------------------------------------------

CCC = g++ -O0
CC  = gcc -O0
JAVAC = javac

# ---------------------------------------------------------------------
# Compiler options
# ---------------------------------------------------------------------

CCOPT = -m64 -O -fPIC -fno-strict-aliasing -fexceptions -DNDEBUG -DIL_STD
COPT  = -m64 -fPIC -fno-strict-aliasing
JOPT  = -classpath $(CPLEXDIR)/lib/cplex.jar -O

# ---------------------------------------------------------------------
# Link options and libraries
# ---------------------------------------------------------------------

CPLEXBINDIR   = $(CPLEXDIR)/bin/$(BINDIST)
CPLEXJARDIR   = $(CPLEXDIR)/lib/cplex.jar
CPLEXLIBDIR   = $(CPLEXDIR)/lib/$(SYSTEM)/$(LIBFORMAT)
CONCERTLIBDIR = $(CONCERTDIR)/lib/$(SYSTEM)/$(LIBFORMAT)

CCLNDIRS  = -L$(CPLEXLIBDIR) -L$(CONCERTLIBDIR)
CLNDIRS   = -L$(CPLEXLIBDIR)
CCLNFLAGS = -lconcert -lilocplex -lcplex -lm -lpthread
CLNFLAGS  = -lcplex -lm -lpthread
JAVA      = java  -d64 -Djava.library.path=$(CPLEXDIR)/bin/x86-64_linux -classpath $(CPLEXJARDIR):


all:
	make all_cpp

execute: all
	make execute_cpp

CONCERTINCDIR = $(CONCERTDIR)/include
CPLEXINCDIR   = $(CPLEXDIR)/include

EXDIR         = $(CPLEXDIR)/examples
EXINC         = $(EXDIR)/include
EXDATA        = $(EXDIR)/data
EXSRCC        = $(EXDIR)/src/c
EXSRCCX       = $(EXDIR)/src/c_x
#EXSRCCPP      = $(EXDIR)/src/cpp
#EXSRCCPP      = /home/trungbq/Documents/FacilityLocation
EXSRCCPP      = /home/stack/IRONIC/Facility-Location-Optimization/estimate
EXSRCJAVA     = $(EXDIR)/src/java

CFLAGS  = $(COPT)  -I$(CPLEXINCDIR)
CCFLAGS = $(CCOPT) -I$(CPLEXINCDIR) -I$(CONCERTINCDIR)
JCFLAGS = $(JOPT)


#------------------------------------------------------------
#  make all      : to compile the examples.
#  make execute  : to compile and execute the examples.
#------------------------------------------------------------


CPP_EX = FL


all_cpp: $(CPP_EX)

execute_cpp: $(CPP_EX)
	 ./Fl


# ------------------------------------------------------------

clean :
	/bin/rm -rf *.o *~ *.class
	/bin/rm -rf $(C_EX) $(CX_EX) $(CPP_EX)
	/bin/rm -rf *.mps *.ord *.sos *.lp *.sav *.net *.msg *.log *.clp

# ------------------------------------------------------------
#
# The examples
#

FL: Main.o
	$(CCC) $(CCFLAGS) $(CCLNDIRS) -o FL Main.o $(CCLNFLAGS)
Main.o: $(EXSRCCPP)/main_m.cpp
	$(CCC) -c $(CCFLAGS) $(EXSRCCPP)/main_m.cpp -o Main.o

# Local Variables:
# mode: makefile
# End: