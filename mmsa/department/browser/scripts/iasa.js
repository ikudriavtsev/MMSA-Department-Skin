$(function(){
	$("#metabanner").each(function(){
		$("#metabanner_next").click(function(){
			var 
				holder = $(this).parent().children('.inside'),
				curr = holder.children(".current:not(:animated)")
				next = curr.next();
				
			if(curr.length==0)
				return false;
				
			curr.removeClass('current').css({zIndex:1,display:'block'}).stop().animate({left: -holder.width()-400},1000,function(){$(this).css('display','none')});
			if(next.length == 0)
				next = holder.children("div:first");
			next.addClass("current").css({left: holder.width(),zIndex:2,display:'block'}).stop().animate({left: 0},500);
			
			$("#metabanner>.list>.current").removeClass("current");
			$("#metabanner>.list>a:eq("+next.prevAll().length+")").addClass("current");
			
			return false;
		});
		$("#metabanner_prev").click(function(){
			var 
				holder = $(this).parent().children('.inside'),
				curr = holder.children(".current:not(:animated)")
				prev = curr.prev();
				
			if(curr.length==0)
				return false;
				
			curr.removeClass('current').css({zIndex:1,display:'block'}).stop().animate({left: holder.width()+400},1000,function(){$(this).css('display','none')});
			if(prev.length == 0)
				prev = holder.children("div:last");
			prev.addClass("current").css({left: -holder.width(),zIndex:2,display:'block'}).stop().animate({left: 0},500);
			
			$("#metabanner>.list>.current").removeClass("current");
			$("#metabanner>.list>a:eq("+prev.prevAll().length+")").addClass("current");
			
			return false;
		});
		
		$("#metabanner>.list>a").click(function(){
			var holder = $('#metabanner>.inside');
			$("#metabanner>.inside>.current").removeClass('current').css({zIndex:1,display:'block'}).stop().animate({left: -holder.width()},1000,function(){$(this).css('display','none')});
			$("#metabanner>.inside>div:eq("+$(this).prevAll().length+")").addClass("current").css({left: holder.width(),zIndex:2,display:'block'}).stop().animate({left: 0},500);
			$(this).addClass("current");
			$(this).siblings(".current").removeClass("current");
			return false;
		});
		
		var metabannerTimer = function(){
			$("#metabanner_next").trigger('click');
			timer = setTimeout( metabannerTimer, 10000 );
		},
		timer = setTimeout(metabannerTimer, 10000);
		
		$(this).mouseenter(function(){
			$(this).children("#metabanner_next, #metabanner_prev").stop().animate({opacity: 1},500);
			clearTimeout(timer);
			timer = false;
		})
		.mouseleave(function(){
			$(this).children("#metabanner_next, #metabanner_prev").stop().animate({opacity: .2},500);
			if( !timer )
				timer = setTimeout(metabannerTimer, 5000);
		})
		$(this).children("#metabanner_next, #metabanner_prev").css('opacity',.2);
	})
	$("ul.menu").each(function(){
		$(this).children().each(function(){
			if( $(this).hasClass("curr") ){
				$(this).removeClass("curr").addClass("nowel").addClass("pageel")
					.children("a").css({top:6, opacity: .7});
				$("<div class='jsBg'><div class='sel'><a></a></div></div>").appendTo(this);
				
				$(this).children(".secondMenu").css({display: 'block', marginTop: 7})
					.children().css({ left: 0, top: 0 })
					.wrap("<div>").parent().css({height: 23, marginLeft: 15, overflow: 'hidden', background: 'none', padding: 0, width: $(this).children(".secondMenu").width()-20})
			}
			else{
				$("<div class='jsBg'><div class='sel'><a></a></div></div>").appendTo(this)
					.children().css({top: 28});
				
				$(this).children(".secondMenu").css({display: 'block', marginTop: 7}).hide()
					.children().css({ left: 0, top: -23 })
					.wrap("<div>").parent().css({height: 23, marginLeft: 15, overflow: 'hidden', background: 'none', padding:0, width: $(this).children(".secondMenu").width()-20})
			}
		})
		.children("a").bind('mouseenter', function(){
			if( $(this).parent().hasClass("nowel") )
				return true;
			
			$("ul.menu>li.nowel").each(function(){
				$(this).removeClass("nowel")
					.children("a").stop().animate({top: 0, opacity: 1}, 200).end()
					.children(".jsBg").children().stop().animate({top: 28},200);
				
				$(this).children(".secondMenu").hide().children().children().stop().animate({top: -23},200,
					function(){$(this).parents(".secondMenu").hide()});
			});
			
			$(this).stop().animate({top: 6, opacity: .7}, 200)
				.parent().addClass("nowel")
				.children(".jsBg").children().stop().animate({top: 5},200);
			
			var sm = $(this).parent().children(".secondMenu");
			
			sm.css({marginLeft: 0}).show().children().children().stop().animate({top: -23},200).animate({top: 0},200);
			
			sm.css({marginLeft: 
				sm.children().offset().left < 20 ?
					20-sm.children().offset().left :
					Math.min($(".page").width() - 20 - sm.children().offset().left - sm.children().width(), 0)
			});
			return false;
		});
		
		$(this).bind({ 
			mouseleave: function(){
				$(this).data('timer',setTimeout(function(){
					var now = $('ul.menu>li.pageel a');
					if( now.length>0 )
						now.trigger('mouseenter');
					else
						$("ul.menu>li.nowel").each(function(){
							$(this).removeClass("nowel")
								.children("a").stop().animate({top: 0, opacity: 1}, 200).end()
								.children(".jsBg").children().stop().animate({top: 28},200);
							
							$(this).children(".secondMenu").hide().children().children().stop().animate({top: -23},200,
								function(){$(this).parents(".secondMenu").hide()});
						});
				}, 700));
			},
			mouseenter: function(){
				if( $(this).data('timer') )
					clearTimeout($(this).data('timer'));
				$(this).data('timer',null);
			}
		});
		
		$(window).resize(function() {
			var sm = $("ul.menu>li.nowel>.secondMenu").css({marginLeft: 0});
			if( !sm.length )
				return;
			sm.css({marginLeft: 
				sm.children().offset().left < 20 ?
					20-sm.children().offset().left :
					Math.min($(".page").width() - 20 - sm.children().offset().left - sm.children().width(), 0)
			});
		}).trigger('resize');
	});
	$("#courses").each(function(){
		$("#courses>.stages a").click(function(){
			$("#courses>.stages .selected").removeClass('selected');
			var pos = $(this).parents('td').addClass('selected').prevAll().length;
			$("#courses>.discription").each(function(){
				$(this).css({display: 'block', height: $(this).height(), opacity: 0});
				var h = $(this).children().hide().eq(pos).show().height();
				$(this).animate({opacity: 1, height: h}, 300, function(){ $(this).css({height: 'auto'})});
			});
			return false;
		})
	});
	$(".auth>.login-link").click(function(){
		$("#login-form").fadeIn(300).css('display','table');
		return false;
	});
	$(".bubble>div>div>div>.close").click(function(){
		$(this).parents('.bubble').fadeOut(300);
	})
})