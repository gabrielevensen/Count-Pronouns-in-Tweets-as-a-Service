from celery import Celery
from flask import Flask, render_template
import json
import os
import timeit
import re



def find_word(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def make_celery(app):
    celery = Celery(app.import_name, backend='rpc://',
                    broker='pyamqp://guest@localhost//')
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = Flask(__name__)
celery = make_celery(app)


# -------- Flask Test -------- #
# Returns entered name
@app.route('/')
def process1():
    return render_template('welcome.html')


# -------- *1* Run Tweet Counter in Flask -------- #
@app.route('/start_count')
def process():
    result = word_counter.delay()
    # time.sleep(10)
    return render_template('test.html', results=result.get())

@app.route('/start_count/bar_plot')
def process2():
    return render_template('barplot.html')


# -------- *1* Present result in Flask -------- #
@celery.task(name='worker1.word_counter')
def word_counter():
    start = timeit.default_timer()

    han_counter = 0
    hon_counter = 0
    den_counter = 0
    det_counter = 0
    denna_counter = 0
    denne_counter = 0
    hen_counter = 0
    unique_counter = 0

    for subdir, dirs, files in os.walk('data'):
        for file in files:
            filepath = subdir + os.sep + file
            fil = open(filepath, 'r')

            lines = fil.readlines()
            for index, line in enumerate(lines):
                if index % 2 == 0 and 'retweeted_status' not in json.loads(line.strip()):
                    if find_word('han')(json.loads(line.strip())['text']) is not None:
                        han_counter += 1
                    if find_word('hon')(json.loads(line.strip())['text']) is not None:
                        hon_counter += 1
                    if find_word('den')(json.loads(line.strip())['text']) is not None:
                        den_counter += 1
                    if find_word('det')(json.loads(line.strip())['text']) is not None:
                        det_counter += 1
                    if find_word('denna')(json.loads(line.strip())['text']) is not None:
                        denna_counter += 1
                    if find_word('denne')(json.loads(line.strip())['text']) is not None:
                        denne_counter += 1
                    if find_word('hen')(json.loads(line.strip())['text']) is not None:
                        hen_counter += 1
                    unique_counter += 1

    fil.close()


    # Code for creating the plot.
    # objects = ('Han', 'Hon', 'Den', 'Det', 'Denna', 'Denne', 'Hen')
    # y_pos = np.arange(len(objects))
    # performance = [han_counter / unique_counter, hon_counter / unique_counter,
    #                den_counter / unique_counter, det_counter / unique_counter,
    #                denna_counter / unique_counter, denne_counter / unique_counter,
    #                hen_counter / unique_counter]
    #
    # plt.bar(y_pos, performance, align='center', alpha=1)
    # plt.xticks(y_pos, objects)
    # plt.title('Frequencies of pronouns normalized by total number of unique tweets')
    # plt.ylabel('Frequencies')
    # plt.title('Pronouns')
    # plt.grid(axis='y')
    # plt.show()

    stop = timeit.default_timer()
    timer = stop - start

    pronouns = ['han', 'hon', 'den', 'det', 'denna', 'denne', 'hen', 'Total unique tweets',
                'Time for finding pronouns in seconds']
    counter = [han_counter, hon_counter, den_counter, det_counter, denna_counter, denne_counter, hen_counter,
               unique_counter, timer]
    result = dict(zip(pronouns, counter))

    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
