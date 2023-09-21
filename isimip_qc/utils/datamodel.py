import subprocess


def call_cdo(args, input_file, output_file):
    args = ['cdo', *args, str(input_file), str(output_file)]
    # print(' '.join(args))
    subprocess.check_call(args)


def call_nccopy(args, input_file, output_file):
    args = ['nccopy', *args, str(input_file), str(output_file)]
    # print(' '.join(args))
    subprocess.check_call(args)
