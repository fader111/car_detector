#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
a=0

if __name__ == '__main__':
	if 'win' in sys.platform:
		from camera import Camera
		print "Windows mode"
	else:
		from camera_pi import Camera

