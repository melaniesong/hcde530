def count_words(text):
    return len(text.split())


reviews = [
    "Love the clean layout and how quickly everything loads.",
    "Great idea but the onboarding steps felt confusing at first.",
    "I use this every day to track my routines and reminders.",
    "Notifications are helpful without being too annoying or frequent.",
    "The latest update fixed bugs and made scrolling much smoother.",
    "Search works well, but filters could be more detailed.",
    "I like the dark mode and the readable font sizes.",
    "Please add an export option for my weekly progress data.",
    "The app crashes sometimes when I upload a large photo.",
    "Simple interface, strong functionality, and very little learning curve.",
    "I finished setup in minutes and started using it right away.",
    "The free version is solid, though premium feels expensive.",
    "Customer support replied quickly and solved my issue politely.",
    "Sync between phone and tablet has been reliable so far.",
    "I wish there were more color themes and icon choices.",
    "Performance is fast even when my internet connection is weak.",
    "This app helped me stay organized during a busy semester.",
    "Some buttons are too small and hard to tap accurately.",
    "Great for beginners who want straightforward tools without clutter.",
    "I had trouble resetting my password from the profile screen.",
    "The tutorial videos were clear and easy to follow.",
    "Data visualizations are useful, especially the weekly trend chart.",
    "I appreciate the accessibility options and larger text settings.",
    "Offline mode works, but syncing later can take a while.",
    "The calendar view is excellent for planning upcoming tasks.",
    "Please let users customize notification sounds and vibration patterns.",
    "I accidentally deleted an item and could not undo it.",
    "The app feels polished and professional compared to competitors.",
    "Loading times improved a lot after the recent patch.",
    "I would recommend this to classmates managing group projects.",
    "Sharing reports with teammates is quick and convenient.",
    "The sign in process should support more authentication options.",
    "I like how the dashboard summarizes my activity clearly.",
    "Sometimes the keyboard covers input fields on smaller screens.",
    "The help center articles answered most of my questions.",
    "Great app overall, but there are occasional lag spikes.",
    "I enjoy the progress badges because they keep me motivated.",
    "Please add reminders based on location and time together.",
    "Setup was intuitive and I did not need instructions.",
    "The app drains battery faster than my other tools.",
    "I can quickly find past entries using the search bar.",
    "Collaboration features are useful for team based assignments.",
    "I wish charts had labels that were easier to read.",
    "This app has made my workflow much more consistent.",
    "Push notifications stopped working after I changed phone settings.",
    "The typography and spacing make content comfortable to scan.",
    "I like that I can reorder tasks with drag and drop.",
    "Exported files opened correctly and matched what I expected.",
    "It would help to have keyboard shortcuts on desktop.",
    "Overall, this is dependable and worth using every week.",
]


word_counts = []

print(f"{'Review #':<9} {'Words':<5} Review")
print("-" * 80)

for i, review in enumerate(reviews, start=1):
    count = count_words(review)
    word_counts.append(count)
    print(f"{i:<9} {count:<5} {review}")

print("\nSummary")
print("-" * 80)
print(f"Total responses: {len(word_counts)}")
print(f"Shortest: {min(word_counts)} words")
print(f"Longest: {max(word_counts)} words")
print(f"Average: {sum(word_counts) / len(word_counts):.1f} words")
