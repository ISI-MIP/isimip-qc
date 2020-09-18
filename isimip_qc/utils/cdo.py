import subprocess


def call_cdo(args, input_file, output_file):
    args = ['cdo'] + args + [str(input_file), str(output_file)]
    print(' '.join(args))
    subprocess.check_call(args)
