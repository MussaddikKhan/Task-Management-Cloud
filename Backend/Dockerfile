FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install them into the Lambda task root
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copy the rest of your backend code
COPY . ${LAMBDA_TASK_ROOT}

# Tell Lambda to look inside the 'app' folder for main.py
CMD ["main.handler"]