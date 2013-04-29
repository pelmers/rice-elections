"""
Google App Engine tasks.
"""
import logging
import json
from datetime import timedelta
from google.appengine.api import taskqueue

def schedule_result_computation(election, task_url):
    method_name = "compute_results"
    old_task_name = '-'.join(
        [str(election.key()), str(election.task_count), method_name])
    election.task_count += 1
    task_name = '-'.join(
        [str(election.key()), str(election.task_count), method_name])

    # Delete any existing tasks enqueued for computing results
    q = taskqueue.Queue()
    q.delete_tasks(taskqueue.Task(name=old_task_name))

    # Enqueue new task for computing results after election ends
    compute_time = election.end + timedelta(seconds=5)
    data = {'election_key': str(election.key()),
            'method': method_name}
    retry_options = taskqueue.TaskRetryOptions(task_retry_limit=0)
    taskqueue.add(name=task_name,
                  url=task_url,
                  params={'data': json.dumps(data)},
                  eta=compute_time,
                  retry_options=retry_options)
    election.put()
    logging.info('Election result computation enqueued.')
