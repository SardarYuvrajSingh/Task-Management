import io
import matplotlib.pyplot as plt
import pandas as pd

def test_plot():
    data = {'completed_day': ['2023-01-01', '2023-01-02', '2023-01-03'], 'count': [3, 5, 2]}
    df = pd.DataFrame(data)
    
    df['completed_day'] = pd.to_datetime(df['completed_day'])
    df['completed_day'] = df['completed_day'].dt.date
    task_counts = df.groupby('completed_day').size()

    fig = plt.figure(figsize=(10, 6))
    task_counts.plot(kind='bar', color='skyblue')
    plt.title('Tasks Completed per Day', fontsize=16)
    plt.xlabel('Day', fontsize=12)
    plt.ylabel('Number of Tasks', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close(fig)
    return img_buffer
