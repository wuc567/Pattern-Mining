# Makefile
CXX = g++
CXXFLAGS = -std=c++17 -I ./libsdsl/include/ -msse3 -O3 -fomit-frame-pointer -funroll-loops
#-DVISUALIZATION


LDFLAGS = -L ./libsdsl/lib/
LIBS = -lsdsl -ldivsufsort -ldivsufsort64




%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@


# OPST construction

ConstructionSOURCES = OPST_construction.cpp node.cpp OPST.cpp utils.cpp
ConstructionOBJECTS = $(ConstructionSOURCES:.cpp=.o)
ConstructionTARGET = OPSTConstruction


$(ConstructionTARGET): $(ConstructionOBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)



clean_OPSTConstruction:
	rm -f $(ConstructionTARGET) $(ConstructionOBJECTS)




# OPST + mining maximal patterns


maximalOPSTSOURCES = OPST_MP.cpp node.cpp OPST.cpp utils.cpp
maximalOPSTOBJECTS = $(maximalOPSTSOURCES:.cpp=.o)
maximalOPSTTARGET = OPSTMaximal




$(maximalOPSTTARGET): $(maximalOPSTOBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)



clean_OPSTMaximal:
	rm -f $(maximalOPSTTARGET) $(maximalOPSTOBJECTS)






# OPST + mining closed patterns


closedOPSTSOURCES = OPST_CP.cpp node.cpp OPST.cpp utils.cpp
closedOPSTOBJECTS = $(closedOPSTSOURCES:.cpp=.o)
closedOPSTTARGET = OPSTClosed



$(closedOPSTTARGET): $(closedOPSTOBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)


clean_OPSTClosed:
	rm -f $(closedOPSTTARGET) $(closedOPSTOBJECTS)











# baseline for mining maximal patterns

BAMPSOURCES = BA_MP.cpp baseline.cpp utils.cpp
BAMPOBJECTS = $(BAMPSOURCES:.cpp=.o)
BAMPTARGET = BAMP



$(BAMPTARGET): $(BAMPOBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)


clean_BAMP:
	rm -f $(BAMPTARGET) $(BAMPOBJECTS)



# baseline for mining closed patterns


BACPSOURCES = BA_CP.cpp baseline.cpp utils.cpp
BACPOBJECTS = $(BACPSOURCES:.cpp=.o)
BACPTARGET = BACP



$(BACPTARGET): $(BACPOBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)



clean_BACP:
	rm -f $(BACPTARGET) $(BACPOBJECTS)






# OPMS with suffix links


OPST_MS_SOURCES = OPST_MS_SuffixLink.cpp node.cpp OPST_MS.cpp utils.cpp oracle.cpp DerivedWTInt.cpp baseline.cpp
OPST_MS_OBJECTS = $(OPST_MS_SOURCES:.cpp=.o)
OPST_MS_TARGET = OPST_MS_SuffixLink



$(OPST_MS_TARGET): $(OPST_MS_OBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)



clean_OPST_MS_SuffixLink:
	rm -f $(OPST_MS_TARGET) $(OPST_MS_OBJECTS)




# OPMS without suffix links

OPST_MS_Root_SOURCES = OPST_MS_Root.cpp node.cpp OPST_MS.cpp utils.cpp oracle.cpp DerivedWTInt.cpp baseline.cpp
OPST_MS_Root_OBJECTS = $(OPST_MS_Root_SOURCES:.cpp=.o)
OPST_MS_Root_TARGET = OPST_MS_Root




$(OPST_MS_Root_TARGET): $(OPST_MS_Root_OBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)


clean_OPST_MS_Root:
	rm -f $(OPST_MS_Root_TARGET) $(OPST_MS_Root_OBJECTS)




all: $(ConstructionTARGET) $(maximalOPSTTARGET) $(closedOPSTTARGET) $(BAMPTARGET) $(BACPTARGET) $(OPST_MS_TARGET) $(OPST_MS_Root_TARGET)



clean: clean_OPSTConstruction clean_OPSTMaximal clean_OPSTClosed clean_BAMP clean_BACP clean_OPST_MS_SuffixLink clean_OPST_MS_Root


.PHONY: all clean clean_OPSTConstruction clean_OPSTMaximal clean_OPSTClosed clean_BAMP clean_BACP clean_OPST_MS_SuffixLink clean_OPST_MS_Root
