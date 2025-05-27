const navbar = document.querySelector('header');
const content = document.querySelector('#newsDetailOverlay');

const navHeight = navbar.offsetHeight;

const computedHeight = `calc(100vh - ${navHeight}px)`;

content.style.setProperty("height", computedHeight, "important");

let page = 1;
let isLoading = false;
const loggedInUser = document.getElementById('loggedInUser').value;
const loggedInUserId = document.getElementById('loggedInUserId').value;

// News detail overlay elements
const newsDetailOverlay = document.getElementById('newsDetailOverlay');
const newsDetailContent = document.getElementById('newsDetailContent');
const closeDetailBtn = document.getElementById('closeDetailBtn');
const is_authenticated = document.getElementById('is_authenticated').value

function showNewsDetail(newsId) {
    fetch(`/news/${newsId}/`)  // You'll need to create this endpoint
        .then(response => response.json())
        .then(data => {
            newsDetailContent.innerHTML = `
                    <h1 class="text-3xl font-bold mb-4">${data.title}</h1>
                    <div id="carousel-${data}" class="relative rounded-lg overflow-hidden shadow-lg" data-carousel="static">
                        <div class="relative" data-carousel-inner>
                            ${data.images.map(image => `
                                <div class="hidden duration-700 ease-in-out" data-carousel-item>
                                    <img src="${image.image}" class="object-cover w-full h-full" alt="Slide">
                                </div>
                            `).join('')}
                        </div>
                        ${data.images.length > 1 ? `
                            <button type="button" class="flex absolute top-1/2 left-3 z-40 items-center justify-center w-10 h-10 bg-gray-200/50 rounded-full hover:bg-gray-300 focus:outline-none transition" data-carousel-prev>
                                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                                </svg>
                            </button>
                            <button type="button" class="flex absolute top-1/2 right-3 z-40 items-center justify-center w-10 h-10 bg-gray-200/50 rounded-full hover:bg-gray-300 focus:outline-none transition" data-carousel-next>
                                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                </svg>
                            </button>
                        ` : ''}
                    </div>
                    <div class="prose max-w-none">${data.content}</div>
                    <div class="flex items-center mt-8 gap-2">
                        <img src="${data.author.userprofile.profile_picture}" class="h-12 w-12 rounded-full" alt="">
                        <div>
                            <a href="/profile/${data.author.username}" class="font-medium">${data.author.userprofile.full_name}</a>
                            <div class="text-sm text-neutral-600">${data.author.followers} Subscribers</div>
                        </div>
                        ${loggedInUser !== data.author.username ? `
                            <button id="follow-btn-detail" data-user-id="${data.author.id}" data-is-following="${data.author.is_following}" class="bg-black text-white px-3 py-1 rounded-xl ml-auto">
                                ${data.author.is_following ? 'Unfollow' : 'Follow'}
                            </button>
                        ` : ''}
                    </div>
                    
                `;
            fetch(`/news/${newsId}/comments/`)
                .then(response => response.json())
                .then(response => {
                    const comments = response.comments;
                    comments_container = document.createElement('div')
                    comments_container.innerHTML = `
                        <div class="comments-section">
                            <h2 class="text-2xl font-bold mb-4">Comments(${data.comments_count})</h2>
                            <div class="comments-list space-y-4 mb-4">
                                ${comments.map(comment => `
                                    <div class="comment flex items-start gap-3">
                                        <img src="${comment.author.profile_picture}" class="w-8 h-8 rounded-full" />
                                        <div>
                                            <div class="font-medium">${comment.author.full_name}</div>
                                            <div class="text-gray-600">${comment.text}</div>
                                            <div class="text-xs text-gray-400">${comment.created_at}</div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                            ${is_authenticated == "True" ? `                            
                            <div class="comment-form">
                                <form id="postCommentForm" class="flex gap-2">
                                    <input type="text" name="text" placeholder="Add a comment..." 
                                        class="flex-1 p-2 border rounded-lg" required />
                                    <button type="submit" class="bg-black text-white px-4 py-2 rounded-lg">
                                        Post
                                    </button>
                                </form>
                            </div>
                            `: `<div class='text-red-500 p-2'>You have to login first to add comments</div>`}
                        </div>
                        
                    `;
                    newsDetailContent.appendChild(comments_container)
                    if (is_authenticated == "True") {
                        document.getElementById('postCommentForm').addEventListener('submit', (e) => {
                            e.preventDefault();
                            const formData = new FormData(e.target);
                            fetch(`/news/${newsId}/comments/post/`, {
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': getCookie('csrftoken'),
                                },
                                body: formData,
                            })
                                .then(response => response.json())
                                .then(comment => {
                                    const commentsList = document.querySelector('.comments-list');
                                    commentsList.insertAdjacentHTML('afterbegin', `
                                    <div class="comment flex items-start gap-3">
                                        <img src="${comment.author.profile_picture}" class="w-8 h-8 rounded-full" />
                                        <div>
                                            <div class="font-medium">${comment.author.full_name}</div>
                                            <div class="text-gray-600">${comment.text}</div>
                                            <div class="text-xs text-gray-400">${comment.created_at}</div>
                                        </div>
                                    </div>
                                `);
                                    e.target.reset();

                                    // Update comment count
                                    const commentCount = document.querySelector(`.comment-btn[data-news-id="${newsId}"] span`);
                                    commentCount.textContent = parseInt(commentCount.textContent) + 1;
                                });
                        });
                    }



                })
            // Initialize follow button in detail view
            const followBtnDetail = document.getElementById('follow-btn-detail');
            if (followBtnDetail) {
                followBtnDetail.addEventListener('click', handleFollow);
            }
            let carousel = document.getElementById(`carousel-${data}`);
            initializeCarousel(carousel);
            newsDetailOverlay.style.display = 'block';
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            console.error('Error loading news detail:', error);
        });
}

function closeNewsDetail() {
    newsDetailOverlay.style.display = 'none';
    document.body.style.overflow = 'auto';
}

closeDetailBtn.addEventListener('click', closeNewsDetail);

function handleFollow(event) {
    const button = event.currentTarget;
    const userId = button.getAttribute('data-user-id');
    const isFollowing = button.getAttribute('data-is-following') === 'true';
    const url = '/toggle_follow/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ user_id: userId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                button.textContent = data.action === 'followed' ? 'Unfollow' : 'Follow';
                button.setAttribute('data-is-following', data.action === 'followed');

                // Update follower count if needed
                const followerCountElement = button.closest('.flex.items-center').querySelector('.text-neutral-600');
                if (followerCountElement) {
                    const currentCount = parseInt(followerCountElement.textContent.split(' ')[0]);
                    followerCountElement.textContent = `${data.action === 'followed' ? currentCount + 1 : currentCount - 1} Subscribers`;
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function loadMoreNews(excludeId = null) {
    if (isLoading) return;
    isLoading = true;

    let url = `/news/?page=${page}`;
    if (excludeId) {
        url += `&exclude=${excludeId}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const results = data.results;

            if (!results || results.length === 0) {
                console.log('No more news to load.');
                isLoading = true; // Lock it to prevent further loading
                return;
            }
            if (data.results.length > 0) {
                const shortsContainer = document.getElementById('shortsContainer');

                data.results.forEach(item => {
                    const newsItem = document.createElement('div');
                    const isAuthor = loggedInUser === item.author.username;
                    const isFollowing = item.author.is_following;
                    newsItem.className = 'relative short min-h-full p-4 flex flex-col align-middle justify-between';
                    newsItem.innerHTML = `
                            <div class="font-medium text-xl mb-2">${item.title}</div>
                            <div id="default-carousel" class="relative rounded-lg overflow-hidden shadow-lg" data-carousel="static">
                                <div class="relative h-40" data-carousel-inner>
                                    ${item.images.map(image => `
                                        <div class="hidden duration-700 ease-in-out" data-carousel-item>
                                            <img src="${image.image}" class="object-cover w-full h-full" alt="Slide">
                                        </div>
                                    `).join('')}
                                </div>
                                ${item.images.length > 1 ? `
                                    <button type="button" class="flex absolute top-1/2 left-3 z-40 items-center justify-center w-10 h-10 bg-gray-200/50 rounded-full hover:bg-gray-300 focus:outline-none transition" data-carousel-prev>
                                        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                                        </svg>
                                    </button>
                                    <button type="button" class="flex absolute top-1/2 right-3 z-40 items-center justify-center w-10 h-10 bg-gray-200/50 rounded-full hover:bg-gray-300 focus:outline-none transition" data-carousel-next>
                                        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                                        </svg>
                                    </button>
                                ` : ''}
                            </div>
                            <div>
                                <div class="text-sm overflow-hidden text-ellipsis line-clamp-4 my-2">${item.content}</div>
                                <div>
                                    <a href="#" class="read-more-btn text-blue-400 hover:border-b hover:border-blue-400 inline" data-news-id="${item.id}">Read more.</a>
                                </div>
                            </div>
                            <div class="flex items-center mt-4 gap-2">
                                <img src="${item.author.userprofile.profile_picture}" class="h-10 w-10 rounded-full" alt="">
                                <a href="/profile/${item.author.username}">${item.author.userprofile.full_name} <div class="text-sm text-neutral-600">${item.author.followers} Subscribers</div></a>
                                ${!isAuthor ? `
                                    <button id="follow-btn" data-user-id="${item.author.id}" data-is-following="${isFollowing}" class="bg-black text-white px-2 py-1 rounded-xl">
                                        ${isFollowing ? 'Unfollow' : 'Follow'}
                                    </button>
                                ` : ''}
                            </div>
                            <!-- Action Buttons -->
                                <div class="action-buttons absolute right-4 bottom-20 flex flex-col items-center">
                                    <!-- Like Button -->
                                    <button class="like-btn flex flex-row items-center " data-news-id="${item.id}" data-liked="${item.is_liked}">
                                        <svg class="w-10 h-10 p-2 rounded-full ${item.is_liked ? 'bg-red-200' : 'bg-gray-100'} hover:bg-gray-200 ${item.is_liked ? 'text-red-500' : 'text-black'} fill-current" viewBox="0 0 24 24">
                                            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                                        </svg>
                                        <span class="text-sm font-bold">${item.likes_count}</span>
                                    </button>

                                    <!-- Comment Button -->
                                    <button class="comment-btn flex flex-col items-center" data-news-id="${item.id}">
                                        <svg class="w-10 h-10 p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-black fill-current" viewBox="0 0 24 24">
                                            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                                        </svg>
                                        <span class="text-sm font-bold">${item.comments_count}</span>
                                    </button>

                                    <!-- Share Button -->
                                    <button class="share-btn flex flex-col items-center" data-news-id="${item.id}">
                                        <svg class="w-10 h-10 p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-black fill-current" viewBox="0 0 24 24">
                                            <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92c0-1.61-1.31-2.92-2.92-2.92zM18 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM6 13c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm12 7.02c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
                                        </svg>
                                    </button>
                                </div>
                        `;
                    shortsContainer.appendChild(newsItem);
                    // // Add these inside the newsItem creation code
                    const likeBtn = newsItem.querySelector('.like-btn');
                    likeBtn.addEventListener('click', handleLikeClick);

                    const commentBtn = newsItem.querySelector('.comment-btn');
                    commentBtn.addEventListener('click', handleCommentClick);

                    const shareBtn = newsItem.querySelector('.share-btn');
                    shareBtn.addEventListener('click', handleShareClick);
                    // Initialize carousel
                    const carouselElement = newsItem.querySelector('[data-carousel="static"]');
                    if (carouselElement) {
                        initializeCarousel(carouselElement);
                    }

                    // Add click event to read more button
                    const readMoreBtn = newsItem.querySelector('.read-more-btn');
                    readMoreBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        showNewsDetail(item.id);
                    });

                    // Add click event to follow button
                    const followBtn = newsItem.querySelector('#follow-btn');
                    if (followBtn) {
                        followBtn.addEventListener('click', handleFollow);
                    }
                });
                page++;
            }
            isLoading = false;
        })
        .catch(error => {
            console.error('Error loading more news:', error);
            isLoading = false;
        });
}

function initializeCarousel(carouselElement) {
    const inner = carouselElement.querySelector('[data-carousel-inner]');
    const items = inner.querySelectorAll('[data-carousel-item]');
    const prevBtn = carouselElement.querySelector('[data-carousel-prev]');
    const nextBtn = carouselElement.querySelector('[data-carousel-next]');

    let currentIndex = 0;

    const showSlide = (index) => {
        items.forEach((item, i) => {
            item.classList.toggle('hidden', i !== index);
        });
    };

    const handlePrev = () => {
        currentIndex = (currentIndex - 1 + items.length) % items.length;
        showSlide(currentIndex);
    };

    const handleNext = () => {
        currentIndex = (currentIndex + 1) % items.length;
        showSlide(currentIndex);
    };

    if (prevBtn) prevBtn.addEventListener('click', handlePrev);
    if (nextBtn) nextBtn.addEventListener('click', handleNext);

    // Show the first slide initially
    showSlide(0);
}

// Script for shorts navigation
const shortsContainer = document.getElementById('shortsContainer');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

let shortsCurrentIndex = 0;

function scrollToShort(index) {
    const shorts = document.querySelectorAll('.short');
    if (index >= 0 && index < shorts.length) {
        shorts[index].scrollIntoView({ behavior: 'smooth' });
        shortsCurrentIndex = index;
    }
}

nextBtn.addEventListener('click', () => scrollToShort(shortsCurrentIndex + 1));
prevBtn.addEventListener('click', () => scrollToShort(shortsCurrentIndex - 1));

// Adjust content height
function adjustContentHeight() {
    const navbar = document.querySelector('header');
    const content = document.querySelector('main');

    if (!navbar || !content) {
        console.error("Navbar or main element not found!");
        return;
    }

    const navHeight = navbar.offsetHeight;
    const computedHeight = `calc(100vh - ${navHeight}px)`;

    content.style.setProperty("height", computedHeight, "important");
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(adjustContentHeight, 100);

    const urlParams = new URLSearchParams(window.location.search);
    const highlightedId = urlParams.get('highlighted');

    if (highlightedId) {
        console.log('Loading highlighted news:', highlightedId);
        fetch(`/news/${highlightedId}/`)
            .then(res => res.json())
            .then(news => {
                displayNewsItem(news); // Display first manually selected item
                page = 1; // Reset page
                loadMoreNews(highlightedId); // Then load rest excluding highlighted
            })
            .catch(error => {
                console.error('Failed to load highlighted news:', error);
                loadMoreNews(); // Fallback to normal
            });
    } else {
        loadMoreNews(); // Load normally
    }
});

window.addEventListener('resize', adjustContentHeight);


// Like Button Handler
function handleLikeClick(e) {
    const button = e.currentTarget;
    const newsId = button.getAttribute('data-news-id');
    const isLiked = button.getAttribute('data-liked') === 'true';
    const is_authenticated = document.getElementById('is_authenticated').value
    if (is_authenticated == 'False') {
        addNotification('You need to login first', 'red')
        return
    }
    fetch(`/news/${newsId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const newIsLiked = data.action === 'like';
                button.setAttribute('data-liked', newIsLiked);
                const likeCount = data.likes;
                button.querySelector('span').textContent = likeCount;

                const svg = button.querySelector('svg');
                svg.classList.toggle('text-red-500', newIsLiked);
                svg.classList.toggle('text-black', !newIsLiked);
                svg.classList.toggle('bg-red-200', newIsLiked);
                svg.classList.toggle('bg-gray-100', !newIsLiked);
            } else if (data.status == "Not authenticated") {
                addNotification('You need to login first', 'red')
            }
        })
        .catch(console.error);
}

// Comment Button Handler
function handleCommentClick(e) {
    const newsId = e.currentTarget.getAttribute('data-news-id');
    fetch(`/news/${newsId}/comments/`)
        .then(response => response.json())
        .then(data => {
            const comments = data.comments;
            newsDetailContent.innerHTML = `
            <div class="comments-section">
                <h2 class="text-2xl font-bold mb-4">Comments</h2>
                <div class="comments-list space-y-4 mb-4">
                    ${comments.map(comment => `
                        <div class="comment flex items-start gap-3">
                            <img src="${comment.author.profile_picture}" class="w-8 h-8 rounded-full" />
                            <div>
                                <div class="font-medium">${comment.author.full_name}</div>
                                <div class="text-gray-600">${comment.text}</div>
                                <div class="text-xs text-gray-400">${comment.created_at}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                ${is_authenticated == "True" ? `                            
                <div class="comment-form">
                    <form id="postCommentForm" class="flex gap-2">
                        <input type="text" name="text" placeholder="Add a comment..." 
                            class="flex-1 p-2 border rounded-lg" required />
                        <button type="submit" class="bg-black text-white px-4 py-2 rounded-lg">
                            Post
                        </button>
                    </form>
                </div>
                `: `<div class='text-red-500 p-2'>You have to login first to add comments</div>`}
            </div>
        `;
            if (is_authenticated == "True") {
                document.getElementById('postCommentForm').addEventListener('submit', (e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    fetch(`/news/${newsId}/comments/post/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: formData,
                    })
                        .then(response => response.json())
                        .then(comment => {
                            const commentsList = document.querySelector('.comments-list');
                            commentsList.insertAdjacentHTML('afterbegin', `
                        <div class="comment flex items-start gap-3">
                            <img src="${comment.author.profile_picture}" class="w-8 h-8 rounded-full" />
                            <div>
                                <div class="font-medium">${comment.author.full_name}</div>
                                <div class="text-gray-600">${comment.text}</div>
                                <div class="text-xs text-gray-400">${comment.created_at}</div>
                            </div>
                        </div>
                    `);
                            e.target.reset();

                            // Update comment count
                            const commentCount = document.querySelector(`.comment-btn[data-news-id="${newsId}"] span`);
                            commentCount.textContent = parseInt(commentCount.textContent) + 1;
                        });
                });
            }
            newsDetailOverlay.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
}

// Share Button Handler
function handleShareClick(e) {
    const newsId = e.currentTarget.getAttribute('data-news-id');
    const url = `${window.location.origin}/news/${newsId}/`;
    navigator.clipboard.writeText(url)
        .then(() => addNotification('Link copied to clipboard!', 'green'))
        .catch(() => alert('Failed to copy link'));
}

shortsContainer.addEventListener('scroll', () => {
    if (
        shortsContainer.scrollTop + shortsContainer.clientHeight >= shortsContainer.scrollHeight - 100
    ) {
        loadMoreNews();
    }
});

function displayNewsItem(item) {
    const shortsContainer = document.getElementById('shortsContainer');
    const newsItem = document.createElement('div');
    const isAuthor = loggedInUser === item.author.username;
    const isFollowing = item.author.is_following;

    newsItem.className = 'relative short min-h-full p-4 flex flex-col align-middle justify-between';

    newsItem.innerHTML = `
        <div class="font-medium text-xl mb-2">${item.title}</div>
            <div id="default-carousel" class="relative rounded-lg overflow-hidden shadow-lg" data-carousel="static">
                <div class="relative h-40" data-carousel-inner>
                    ${item.images.map(image => `
                        <div class="hidden duration-700 ease-in-out" data-carousel-item>
                            <img src="${image.image}" class="object-cover w-full h-full" alt="Slide">
                        </div>
                    `).join('')}
                </div>
                ${item.images.length > 1 ? `
                    <button type="button" class="flex absolute top-1/2 left-3 z-40 items-center justify-center w-10 h-10 bg-gray-200/50 rounded-full hover:bg-gray-300 focus:outline-none transition" data-carousel-prev>
                        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                        </svg>
                    </button>
                    <button type="button" class="flex absolute top-1/2 right-3 z-40 items-center justify-center w-10 h-10 bg-gray-200/50 rounded-full hover:bg-gray-300 focus:outline-none transition" data-carousel-next>
                        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </button>
                ` : ''}
            </div>
            <div>
                <div class="text-sm overflow-hidden text-ellipsis line-clamp-4 my-2">${item.content}</div>
                <div>
                    <a href="#" class="read-more-btn text-blue-400 hover:border-b hover:border-blue-400 inline" data-news-id="${item.id}">Read more.</a>
                </div>
            </div>
            <div class="flex items-center mt-4 gap-2">
                <img src="${item.author.userprofile.profile_picture}" class="h-10 w-10 rounded-full" alt="">
                <a href="/profile/${item.author.username}">${item.author.userprofile.full_name} <div class="text-sm text-neutral-600">${item.author.followers} Subscribers</div></a>
                ${!isAuthor ? `
                    <button id="follow-btn" data-user-id="${item.author.id}" data-is-following="${isFollowing}" class="bg-black text-white px-2 py-1 rounded-xl">
                        ${isFollowing ? 'Unfollow' : 'Follow'}
                    </button>
                ` : ''}
            </div>
            <!-- Action Buttons -->
                <div class="action-buttons absolute right-4 bottom-20 flex flex-col items-center">
                    <!-- Like Button -->
                    <button class="like-btn flex flex-row items-center " data-news-id="${item.id}" data-liked="${item.is_liked}">
                        <svg class="w-10 h-10 p-2 rounded-full ${item.is_liked ? 'bg-red-200' : 'bg-gray-100'} hover:bg-gray-200 ${item.is_liked ? 'text-red-500' : 'text-black'} fill-current" viewBox="0 0 24 24">
                            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                        </svg>
                        <span class="text-sm font-bold">${item.likes_count}</span>
                    </button>

                    <!-- Comment Button -->
                    <button class="comment-btn flex flex-col items-center" data-news-id="${item.id}">
                        <svg class="w-10 h-10 p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-black fill-current" viewBox="0 0 24 24">
                            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                        </svg>
                        <span class="text-sm font-bold">${item.comments_count}</span>
                    </button>

                    <!-- Share Button -->
                    <button class="share-btn flex flex-col items-center" data-news-id="${item.id}">
                        <svg class="w-10 h-10 p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-black fill-current" viewBox="0 0 24 24">
                            <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92c0-1.61-1.31-2.92-2.92-2.92zM18 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM6 13c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm12 7.02c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1z"/>
                        </svg>
                    </button>
                </div>
    `;

    shortsContainer.appendChild(newsItem);

    // Button listeners
    const likeBtn = newsItem.querySelector('.like-btn');
    likeBtn.addEventListener('click', handleLikeClick);

    const commentBtn = newsItem.querySelector('.comment-btn');
    commentBtn.addEventListener('click', handleCommentClick);

    const shareBtn = newsItem.querySelector('.share-btn');
    shareBtn.addEventListener('click', handleShareClick);

    const readMoreBtn = newsItem.querySelector('.read-more-btn');
    readMoreBtn.addEventListener('click', (e) => {
        e.preventDefault();
        showNewsDetail(item.id);
    });

    const followBtn = newsItem.querySelector('#follow-btn');
    if (followBtn) {
        followBtn.addEventListener('click', handleFollow);
    }

    // Carousel init if needed
    const carouselElement = newsItem.querySelector('[data-carousel="static"]');
    if (carouselElement) {
        initializeCarousel(carouselElement);
    }
}
