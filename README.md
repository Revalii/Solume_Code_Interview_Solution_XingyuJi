# Solum Coding Interview – Xingyu Ji

## Overview

Solutions for Solum Coding Interview.

## Instructions to Run Locally

### Requirements

#### Question A–D

- Python 3.11 (recommended)
- pandas

Install:
```bash
pip install pandas
```

#### Question E

##### Backend

- Python 3.11
- FastAPI
- pandas

Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn main:app --reload
```

Backend will be available at:

```bash
http://127.0.0.1:8000
```

API documentation (Swagger UI):

```bash
http://127.0.0.1:8000/docs
```

##### Frontend

- Node.js (v22 or above recommended)
- npm

Install dependencies and run:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at:

```bash
http://localhost:5173
```

### Notes

- Make sure the backend is running before starting the frontend
- The frontend is configured to call the backend at:

```bash
  http://127.0.0.1:8000
```

## Table of Contents

- [Section A – Data Analysis](./Solutions/Section_A/)
    - [Question A](./Solutions/Section_A/Question_A/Question_A.py)
    - [Question B](./Solutions/Section_A/Question_B/Question_B.py)
    - [Question C](./Solutions/Section_A/Question_C/Question_C.py)

- [Section B – Algorithm](./Solutions/Section_B/)
    - [Question D](./Solutions/Section_B/Question_D/Question_D.py)

- [Section C – Full Stack Interview Assignment](./Solutions/Section_C/)
    - [Question E](./Solutions/Section_C/Question_E)

