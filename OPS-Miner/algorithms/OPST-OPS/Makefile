CXX ?= c++
CXXFLAGS ?= -std=c++17 -O3 -msse3 -fomit-frame-pointer -funroll-loops

SOURCE_DIR := official-source
SDSL_DIR := $(SOURCE_DIR)/libsdsl
INCLUDES := -I$(SOURCE_DIR) -I$(SDSL_DIR)/include
LIBRARY_DIRS := -L$(SDSL_DIR)/lib
LIBRARIES := -lsdsl -ldivsufsort -ldivsufsort64

SOURCES := OPST_Frequent.cpp \
	$(SOURCE_DIR)/node.cpp \
	$(SOURCE_DIR)/OPST.cpp \
	$(SOURCE_DIR)/utils.cpp

TARGET := OPSTFrequent

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SOURCES) \
		$(LIBRARY_DIRS) $(LIBRARIES) -o $(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: clean
