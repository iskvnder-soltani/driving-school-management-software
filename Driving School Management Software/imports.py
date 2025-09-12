import os
import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
from fpdf import FPDF
from PIL import Image, ImageTk  # Add this import for image handling
from functools import partial
import re

DB_FILE = 'Iskander_driving_school.db'
