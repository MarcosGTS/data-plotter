import argparse
import matplotlib.pyplot as plt
import numpy as np
import json
import datetime
import os

# plot -l [listagem] file
# plot -a [atribute name] file
# plot -a [atribute name] file file2 compare results

parser = argparse.ArgumentParser(
    prog='Plotter',
    description='Generate graphs',
    epilog='Made with dedication by Marcos Guilherme')

parser.add_argument("-l", "--list", action="store_true")
parser.add_argument("-o", "--output")
parser.add_argument("-m", "--metric", default="iteration_duration")
parser.add_argument("-f", "--filter", type=int, default=1)
parser.add_argument("filenames", nargs="+")

args = parser.parse_args()
print(args)

def list_attributes(filename):
    metrics = set() 
    with open(filename, "r") as file:
        for line in file:
            obj = json.loads(line)
            if (obj["type"] == "Point"):
                metrics.add(obj["metric"])
    print(metrics)

def generate_plot(ax, metric, filename, output, filter_value = 1):
    # Read a file
    x_axis = []
    y_axis = []

    with open(filename, "r") as file:
        start_time = None 

        counter = 0

        for line in file:

            # Filter data
            counter += 1
            if counter % filter_value != 0: continue
            
            obj = json.loads(line) 
            if obj["type"] == "Point" and obj["metric"] == metric:
                y_axis.append(obj["data"]["value"])

                if not start_time: 
                    start_time = convert_date_timestamp(obj["data"]["time"])

                curr_time = convert_date_timestamp(obj["data"]["time"]) - start_time
                x_axis.append(curr_time)


    return [x_axis, y_axis]

def get_metrics(values):
    max_val = values[0]
    min_val = values[0]
    sum_val = 0

    for n in values: 
        sum_val += n
        if max_val < n: max_val = n
        if min_val > n: min_val = n
    
    avarege = sum_val / len(values)

    acc = 0
    for n in values:
       acc = (n - avarege)**2
    
    standard_diviation = (acc / len(values))**.5

    return {
        "max": round(max_val, 2), 
        "min": round(min_val, 2), 
        "avg": round(avarege, 2), 
        "std": round(standard_diviation, 2)
    }

def format_metrics(metrics):
    result = ""
    for metric in metrics: 
        result += f"{metric} {metrics[metric]}\n"

    return result.strip()


def convert_date_timestamp(date_string):
    date_time = date_string[0:-9]

    if date_time[-1] == ".": date_time += "0"

    dt = datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%f")

    return dt.timestamp()

if args.list:
    list_attributes(args.filenames[0])
else:
    fig, ax = plt.subplots(figsize=(10, 5))             # Create a figure containing a single Axes.
    metric = args.metric 

    # ax.set_title(" X ".join(args.filenames), fontweight="bold")
    ax.set_xlabel("Time (min:sec)")
    ax.set_ylabel(metric)
    ax.xaxis.set_major_formatter(lambda x, pos: f"{(int(x // 60))}:{int(x % 60)}")
    summary = [] 

    for filename in args.filenames:
        [x_axis, y_axis] = generate_plot(ax, metric, filename, args.output, args.filter)

        summary.append(get_metrics(y_axis))

        # y_axis = list(map(lambda x: min(x, 3000.0), y_axis)) # Trucating large values

        ax.plot(x_axis, y_axis, label=filename, alpha=0.6)

    ax.legend()

    for i in range(len(summary)):
        padding = 0.14
        margin = 0.18

        x = (padding + margin * i)
        y = 0.04 

        fontsize = 10 
        text_style = "normal" 
        
        text = format_metrics(summary[i]) 

        color = plt.gca().get_legend().legend_handles[i].get_color()

        plt.gcf().text(x , y, text, 
            fontsize=fontsize, 
            style=text_style,
            color="white",
            fontweight="bold",
            bbox={'facecolor': color, 'alpha': 1, 'pad': 10}
        )

        plt.subplots_adjust(bottom=0.3)

    filepath = "".join(args.filenames[0].split(".")[0:-1])
    filename = os.path.basename(filepath)

    if args.output == None:
        output_name = "".join(args.filenames[0].split(".")[0:-1])
        plt.savefig(output_name + ".jpg")
    else:
        plt.savefig(args.output + "/" + filename + ".jpg")

