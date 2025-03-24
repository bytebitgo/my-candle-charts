export class TVNavigation {
    constructor() {
        this.focusableElements = Array.from(document.querySelectorAll('.tv-focusable'));
        this.currentFocusIndex = -1;
        this.init();
    }

    init() {
        // 初始化焦点
        if (this.focusableElements.length > 0) {
            this.setFocus(0);
        }

        // 监听新添加的可聚焦元素
        const observer = new MutationObserver(() => {
            this.updateFocusableElements();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    updateFocusableElements() {
        this.focusableElements = Array.from(document.querySelectorAll('.tv-focusable'));
    }

    setFocus(index) {
        if (index >= 0 && index < this.focusableElements.length) {
            this.currentFocusIndex = index;
            this.focusableElements[index].focus();
            this.showFocusGuide();
        }
    }

    handleNavigation(direction) {
        const currentElement = this.focusableElements[this.currentFocusIndex];
        if (!currentElement) return;

        const rect = currentElement.getBoundingClientRect();
        let nextIndex = this.currentFocusIndex;

        switch (direction) {
            case 'ArrowUp':
                nextIndex = this.findClosestElement(rect.left + rect.width / 2, rect.top, 'up');
                break;
            case 'ArrowDown':
                nextIndex = this.findClosestElement(rect.left + rect.width / 2, rect.bottom, 'down');
                break;
            case 'ArrowLeft':
                nextIndex = this.findClosestElement(rect.left, rect.top + rect.height / 2, 'left');
                break;
            case 'ArrowRight':
                nextIndex = this.findClosestElement(rect.right, rect.top + rect.height / 2, 'right');
                break;
        }

        if (nextIndex !== this.currentFocusIndex) {
            this.setFocus(nextIndex);
        }
    }

    findClosestElement(x, y, direction) {
        let closest = this.currentFocusIndex;
        let minDistance = Infinity;

        this.focusableElements.forEach((element, index) => {
            if (index === this.currentFocusIndex) return;

            const rect = element.getBoundingClientRect();
            const elementX = rect.left + rect.width / 2;
            const elementY = rect.top + rect.height / 2;

            // 根据方向过滤元素
            switch (direction) {
                case 'up':
                    if (elementY >= y) return;
                    break;
                case 'down':
                    if (elementY <= y) return;
                    break;
                case 'left':
                    if (elementX >= x) return;
                    break;
                case 'right':
                    if (elementX <= x) return;
                    break;
            }

            const distance = Math.sqrt(
                Math.pow(elementX - x, 2) + 
                Math.pow(elementY - y, 2)
            );

            if (distance < minDistance) {
                minDistance = distance;
                closest = index;
            }
        });

        return closest;
    }

    handleSelect() {
        const currentElement = this.focusableElements[this.currentFocusIndex];
        if (currentElement) {
            currentElement.click();
        }
    }

    showFocusGuide() {
        const currentElement = this.focusableElements[this.currentFocusIndex];
        if (!currentElement) return;

        let guide = document.querySelector('.tv-focus-guide');
        if (!guide) {
            guide = document.createElement('div');
            guide.className = 'tv-focus-guide';
            document.body.appendChild(guide);
        }

        const rect = currentElement.getBoundingClientRect();
        guide.style.left = `${rect.right + 10}px`;
        guide.style.top = `${rect.top}px`;
        guide.textContent = this.getElementDescription(currentElement);
        guide.style.opacity = '1';

        setTimeout(() => {
            guide.style.opacity = '0';
        }, 2000);
    }

    getElementDescription(element) {
        if (element.tagName === 'SELECT') {
            return '使用上下键选择，回车确认';
        } else if (element.type === 'number') {
            return '使用上下键调整数值，回车确认';
        } else if (element.type === 'checkbox') {
            return '按回车切换选中状态';
        }
        return '按回车选择';
    }
} 