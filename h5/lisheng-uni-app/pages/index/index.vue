<template>
	<view class="content">
	  <web-view :webview-styles="webviewStyles" src="http://aiportal.h3c.com:40284/"></web-view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				title: 'Hello'
			}
		},
		onLoad() {},
		methods: {}
	}
</script>

<style>
	.webviewStyles{
		height: 100vh !important;
	}
	.content {
		height: 100vh !important;
	}
	iframe{
		height: 100% !important;
	}
</style>
