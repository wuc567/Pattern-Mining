package com.algo.copp.end;


public class MemoryLogger {
	
	private static MemoryLogger instance = new MemoryLogger();

	private double maxMemory = 0;
	
	public static MemoryLogger getInstance(){
		return instance;
	}
	
	public double getMaxMemory() {
		return maxMemory;
	}

	public void reset(){
		maxMemory = 0;
	}
	
	public void checkMemory() {
		double currentMemory = (Runtime.getRuntime().totalMemory() -  Runtime.getRuntime().freeMemory())
				/ 1024d / 1024d;
		if (currentMemory > maxMemory) {
			maxMemory = currentMemory;
		}
	}
}
