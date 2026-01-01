/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ImageLightbox extends Component {
    static template = "royal_estate.ImageLightbox";
    static components = { Dialog };
    static props = {
        images: Array,
        initialIndex: { type: Number, optional: true },
        onSetMain: { type: Function, optional: true },
        onDelete: { type: Function, optional: true },
        close: Function,
    };

    setup() {
        this.state = useState({
            currentIndex: this.props.initialIndex || 0,
        });

        this.onKeyDown = this.onKeyDown.bind(this);

        onMounted(() => {
            document.addEventListener("keydown", this.onKeyDown);
        });

        onWillUnmount(() => {
            document.removeEventListener("keydown", this.onKeyDown);
        });
    }

    get currentImage() {
        return this.props.images[this.state.currentIndex];
    }

    get hasMultipleImages() {
        return this.props.images.length > 1;
    }

    get counter() {
        return `${this.state.currentIndex + 1} / ${this.props.images.length}`;
    }

    onKeyDown(ev) {
        switch (ev.key) {
            case "ArrowLeft":
                ev.preventDefault();
                this.prev();
                break;
            case "ArrowRight":
                ev.preventDefault();
                this.next();
                break;
            case "Escape":
                this.props.close();
                break;
        }
    }

    prev() {
        if (this.state.currentIndex > 0) {
            this.state.currentIndex--;
        } else {
            this.state.currentIndex = this.props.images.length - 1;
        }
    }

    next() {
        if (this.state.currentIndex < this.props.images.length - 1) {
            this.state.currentIndex++;
        } else {
            this.state.currentIndex = 0;
        }
    }

    async setAsMain() {
        if (this.props.onSetMain && this.currentImage) {
            await this.props.onSetMain(this.currentImage.id);
        }
    }

    async deleteImage() {
        if (this.props.onDelete && this.currentImage) {
            const currentId = this.currentImage.id;
            const imagesCount = this.props.images.length;

            await this.props.onDelete(currentId);

            if (imagesCount <= 1) {
                this.props.close();
            } else if (this.state.currentIndex >= imagesCount - 1) {
                this.state.currentIndex = Math.max(0, imagesCount - 2);
            }
        }
    }
}
