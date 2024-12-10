from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Process
import psutil
from datetime import datetime

def terminate_process(pid):
    """Helper function to terminate a process."""
    try:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Process {pid} terminated successfully.")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        print(f"Error terminating process {pid}: {e}")

def get_processes(request):
    processes = []
    
    # Fetch system process details using psutil
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time', 'username']):
        try:
            info = proc.info
            info['start_time'] = datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')

            # Handle missing username
            username = info['username'] if info['username'] else 'Unknown'

            # Save or get the process from the database
            process, created = Process.objects.get_or_create(
                pid=info['pid'],
                defaults={
                    'name': info['name'],
                    'cpu_percent': info['cpu_percent'],
                    'memory_percent': info['memory_percent'],
                    'start_time': info['start_time'],
                    'username': username,  # Ensure a valid username is passed
                }
            )
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        processes = [proc for proc in processes if search_query.lower() in proc['name'].lower() or str(proc['pid']) == search_query]

    # Sort functionality
    sort_key = request.GET.get('sort', '')
    if sort_key in ['cpu_percent', 'memory_percent']:
        processes = sorted(processes, key=lambda x: x[sort_key], reverse=True)

    # Pagination: Set the number of items per page
    paginator = Paginator(processes, 10)  # Show 10 processes per page
    page_number = request.GET.get('page')  # Get the page number from the GET request
    page_obj = paginator.get_page(page_number)  # Get the page object

    # System summary (total CPU and memory usage)
    system_cpu_percent = psutil.cpu_percent(interval=1)
    system_memory = psutil.virtual_memory().percent

    # Handle termination request (POST method)
    if request.method == 'POST':
        pid_to_terminate = request.POST.get('pid')
        if pid_to_terminate:
            print(f"Attempting to terminate process with PID: {pid_to_terminate}")  # Debug log
            terminate_process(int(pid_to_terminate))
            return redirect('process_list')  # Redirect to the same page after termination

    context = {
        'processes': processes,
        'search_query': search_query,
        'system_cpu_percent': system_cpu_percent,
        'system_memory': system_memory,
        'page_obj': page_obj,
    }

    return render(request, 'process-list.html', context)
