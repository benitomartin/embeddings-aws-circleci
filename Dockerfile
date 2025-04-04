FROM public.ecr.aws/lambda/python:3.12.2025.04.01.18

# Set the working directory to /var/task
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY aws_lambda/lambda_function.py ./lambda_function.py

# Command to run the Lambda handler function
CMD [ "lambda_function.lambda_handler" ]
