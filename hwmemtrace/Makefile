CC=gcc
CFLAGS=-O3
LDLIBS=
TARGET=hwmemtrace
SOURCES=hwmemtrace.c
OBJECTS=$(SOURCES:.c=.o)
PREFIX=/usr/local

.PHONY: default all clean check install uninstall

all: $(TARGET) 

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

clean:
	@-rm -f *.o $(TARGET)

install:
	@cp $(TARGET) $(PREFIX)/bin/

uninstall:
	@rm $(PREFIX)/bin/$(TARGET)
