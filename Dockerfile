# Python image
FROM python:3.10

# Workdir
WORKDIR /app

# Requirementsni ko‘chirish va o‘rnatish
COPY requirements.txt .
RUN pip install -r requirements.txt

# Bot fayllarini ko‘chirish
COPY . .

# Botni ishga tushirish
CMD ["python", "my_resume.py"]
