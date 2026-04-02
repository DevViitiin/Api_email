// lib/screens/screens_home/perfil_screen/perfil_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:tabuapp/core/theme/tabu_theme.dart';
import 'package:tabuapp/models/post_model.dart';
import 'package:tabuapp/models/story_model.dart';
import 'package:tabuapp/screens/screens_administrative/administrative_panel/administrative_home/administrative_home.dart';
import 'package:tabuapp/screens/screens_auth/acess_code_screen/acess_code_screen.dart';
import 'package:tabuapp/screens/screens_home/home_screen/home/full_screen_video.dart';
import 'package:tabuapp/screens/screens_home/home_screen/perfis/public_profile_screen.dart';
import 'package:tabuapp/screens/screens_home/home_screen/posts/create_gallery_screen.dart';
import 'package:tabuapp/screens/screens_home/home_screen/posts/story_viewer_screen.dart';
import 'package:tabuapp/screens/screens_home/perfil_screen/perfil/edit_perfil.dart';
import 'package:tabuapp/screens/screens_home/perfil_screen/perfil/perfil_screen_widgets.dart';
import 'package:tabuapp/services/services_administrative/administrative_panel/adm_service.dart';
import 'package:tabuapp/services/services_app/auth_service.dart';
import 'package:tabuapp/services/services_app/cached_avatar.dart';
import 'package:tabuapp/services/services_app/follow_service.dart';
import 'package:tabuapp/services/services_app/perfil_services/gallery_service.dart';
import 'package:tabuapp/services/services_app/perfil_services/media_preload.dart';
import 'package:tabuapp/services/services_app/perfil_services/post_service.dart';
import 'package:tabuapp/services/services_app/post_service.dart';
import 'package:tabuapp/services/services_app/story_service.dart';
import 'package:tabuapp/services/services_app/user_data_notifier.dart';
import 'package:tabuapp/screens/screens_home/home_screen/posts/comments_screen.dart';
import 'package:tabuapp/services/services_app/gallery_service.dart';
import 'package:tabuapp/models/gallery_item_model.dart';
import 'package:tabuapp/screens/screens_home/home_screen/home/full_screen_image.dart';
import 'package:tabuapp/services/services_app/video_preload_service.dart';

class PerfilScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  const PerfilScreen({super.key, required this.userData});

  @override
  State<PerfilScreen> createState() => _PerfilScreenState();
}

class _PerfilScreenState extends State<PerfilScreen>
    with SingleTickerProviderStateMixin {
  late Map<String, dynamic> _localUserData;
  late TabController _tabController;

  // ── Stories ───────────────────────────────────────────────────────────────
  List<StoryModel> _myStories = [];
  bool _loadingStories = true;

  // ── Seguidores (paginado) ─────────────────────────────────────────────────
  List<String> _followers = [];
  int _followersCount = 0;
  bool _loadingFollowers = true;
  bool _loadingMoreFollowers = false;
  bool _hasMoreFollowers = true;
  String? _followersLastKey;

  // ── VIP (paginado) ────────────────────────────────────────────────────────
  List<String> _vipFriends = [];
  int _vipCount = 0;
  bool _loadingVip = true;
  bool _loadingMoreVip = false;
  bool _hasMoreVip = true;
  String? _vipLastKey;

  // ── Galeria ───────────────────────────────────────────────────────────────
  bool _hasGallery = false;
  List<GalleryItem> _galleryItems = [];
  bool _loadingGallery = true;
  Map<String, List<StoryModel>> _stories = {};
  DateTime? _galleryLastCursor;
  bool _loadingMoreGallery = false;
  bool _hasMoreGallery = true;

  // ── Posts ─────────────────────────────────────────────────────────────────
  List<PostModel> _posts = [];
  bool _loadingPosts = true;
  DateTime? _postsLastCursor;
  bool _loadingMorePosts = false;
  bool _hasMorePosts = true;

  bool _isAdmin = false;
  bool _loadingAdmin = true;

  late final String _uid;
  late ScrollController _scrollController;

  @override
  void initState() {
    super.initState();
    final currentUser = FirebaseAuth.instance.currentUser;
    _uid = currentUser?.uid.isNotEmpty == true
        ? currentUser!.uid
        : (widget.userData['uid'] as String? ??
            widget.userData['id'] as String? ??
            '');

    _localUserData = Map<String, dynamic>.from(widget.userData);
    if (UserDataNotifier.instance.value.isEmpty) {
      UserDataNotifier.instance.init(widget.userData);
    }

    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(() => setState(() {}));
    _tabController.addListener(() {
      if (_tabController.indexIsChanging) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (_tabController.index == 1) _carregarGaleria();
        });
      }
    });

    _scrollController = ScrollController();
    _scrollController.addListener(_onScroll);

    _carregarTudo();
    _verificarAdmin();
  }
   void _onScroll() {
    if (_scrollController.position.pixels <
        _scrollController.position.maxScrollExtent * 0.8) return;

    if (_tabController.index == 0) {
      _loadMorePosts();
    } else {
      _loadMoreGallery();
    }
  }

  Future<void> _loadMoreGallery() async {
    if (_loadingMoreGallery || !_hasMoreGallery) return;
    setState(() => _loadingMoreGallery = true);
    try {
      final newItems = await GalleryServicePaginated.instance.fetchItems(
        _uid,
        startAfter: _galleryLastCursor,
      );
      if (newItems.isEmpty) {
        setState(() => _hasMoreGallery = false);
      } else {
        setState(() {
          _galleryItems.addAll(newItems);
          _galleryLastCursor = newItems.last.createdAt;
        });
        if (mounted) {
          await MediaPreloadService.instance.preloadGalleryMedia(
            context,
            newItems,
            userId: _uid,
          );
        }
      }
    } finally {
      if (mounted) setState(() => _loadingMoreGallery = false);
    }
  }
  
  Future<void> _loadMorePosts() async {
    if (_loadingMorePosts || !_hasMorePosts) return;
    setState(() => _loadingMorePosts = true);
    try {
      final newPosts = await PostServicePaginated.instance.fetchPostsByUser(
        _uid,
        startAfter: _postsLastCursor,
      );
      if (newPosts.isEmpty) {
        setState(() => _hasMorePosts = false);
      } else {
        setState(() {
          _posts.addAll(newPosts);
          _postsLastCursor = newPosts.last.createdAt;
        });
        if (mounted) {
          await MediaPreloadService.instance
              .preloadPostsMedia(context, newPosts);
        }
      }
    } finally {
      if (mounted) setState(() => _loadingMorePosts = false);
    }
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    _scrollController.dispose();
    _evictAllPreloads();
    super.dispose();
  }

   void _evictAllPreloads() {
    MediaPreloadService.instance.clearContext('posts_$_uid');
    MediaPreloadService.instance.clearContext('gallery_$_uid');
    MediaPreloadService.instance.clearContext('stories_$_uid');
    debugPrint('[PerfilScreen] 🗑️ Preloads liberados');
  }

  void _preloadGaleriaVideos(List<GalleryItem> items) {
    for (final item in items) {
      if (item.type == 'video') {
        VideoPreloadService.instance.preload(item.id, item.mediaUrl);
      }
    }
  }

  void _evictGaleriaPreloads() {
    for (final item in _galleryItems) {
      if (item.type == 'video') {
        VideoPreloadService.instance.evict(item.id);
      }
    }
  }

  Future<void> _carregarTudo() async {
    await Future.wait([
      _carregarPosts(),
      _carregarStories(),
      _carregarFollowers(),
      _carregarVip(),
      _carregarGaleria(),
    ]);
  }

  Future<void> _verificarAdmin() async {
    setState(() => _loadingAdmin = true);
    final admin = await AdminService.instance.isAdmin(_uid);
    if (mounted) {
      setState(() {
        _isAdmin = admin;
        _loadingAdmin = false;
      });
    }
  }

   Future<void> _carregarPosts() async {
    setState(() {
      _loadingPosts = true;
      _postsLastCursor = null;
      _hasMorePosts = true;
    });
    try {
      final posts =
          await PostServicePaginated.instance.fetchPostsByUser(_uid);
      if (mounted) {
        setState(() {
          _posts = posts;
          _loadingPosts = false;
          if (posts.isNotEmpty) _postsLastCursor = posts.last.createdAt;
          if (posts.length < PostServicePaginated.pageSize) _hasMorePosts = false;
        });
        debugPrint('[PerfilScreen] 🚀 Iniciando preload de ${posts.length} posts...');
        await MediaPreloadService.instance.preloadPostsMedia(context, posts);
        debugPrint('[PerfilScreen] ✅ Preload de posts concluído!');
      }
    } catch (e) {
      debugPrint('[PerfilScreen] ❌ Erro ao carregar posts: $e');
      if (mounted) setState(() => _loadingPosts = false);
    }
  }

   Future<void> _carregarStories() async {
    setState(() => _loadingStories = true);
    try {
      // fetchStoriesByUser é o método correto definido em StoryService
      final stories = await StoryService.instance.fetchStoriesByUser(_uid);
      if (mounted) {
        setState(() {
          _myStories = stories;
          _loadingStories = false;
        });
        // Preload de mídia dos stories (fotos/vídeos)
        if (stories.isNotEmpty) {
          debugPrint('[PerfilScreen] 🚀 Iniciando preload de ${stories.length} stories...');
          await MediaPreloadService.instance.preloadStoriesMedia(
            context,
            stories,
          );
          debugPrint('[PerfilScreen] ✅ Preload de stories concluído!');
        }
      }
    } catch (e) {
      debugPrint('[PerfilScreen] ❌ Erro ao carregar stories: $e');
      if (mounted) setState(() => _loadingStories = false);
    }
  }

  Future<void> _carregarFollowers() async {
    setState(() {
      _loadingFollowers = true;
      _followers = [];
      _followersLastKey = null;
      _hasMoreFollowers = true;
    });
    try {
      final count = await FollowService.instance.getFollowersCount(_uid);
      final page = await FollowService.instance.getFollowersPaginated(_uid);
      if (mounted) {
        setState(() {
          _followersCount = count;
          _followers = page;
          _loadingFollowers = false;
          if (page.isNotEmpty) _followersLastKey = page.last;
          if (page.length < FollowService.pageSize) _hasMoreFollowers = false;
        });
      }
    } catch (e) {
      debugPrint('[PerfilScreen] ❌ Erro ao carregar seguidores: $e');
      if (mounted) setState(() => _loadingFollowers = false);
    }
  }

  Future<void> _carregarVip() async {
    setState(() => _loadingVip = true);
    try {
      final v = await FollowService.instance.getVipFriends(_uid);
      if (mounted) {
        setState(() {
          _vipFriends = v;
          _loadingVip = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loadingVip = false);
    }
  }

  Future<void> _carregarGaleria() async {
    if (_galleryItems.isNotEmpty) return;
    setState(() {
      _loadingGallery = true;
      _galleryLastCursor = null;
      _hasMoreGallery = true;
    });
    try {
      final items = await GalleryServicePaginated.instance.fetchItems(_uid);
      if (mounted) {
        setState(() {
          _galleryItems = items;
          _hasGallery = items.isNotEmpty;
          _loadingGallery = false;
          if (items.isNotEmpty) _galleryLastCursor = items.last.createdAt;
          if (items.length < GalleryServicePaginated.pageSize) {
            _hasMoreGallery = false;
          }
        });
        if (items.isNotEmpty) {
          debugPrint(
              '[PerfilScreen] 🚀 Iniciando preload de ${items.length} itens da galeria...');
          await MediaPreloadService.instance.preloadGalleryMedia(
            context,
            items,
            userId: _uid,
          );
          debugPrint('[PerfilScreen] ✅ Preload de galeria concluído!');
        }
      }
    } catch (e) {
      debugPrint('[PerfilScreen] ❌ Erro ao carregar galeria: $e');
      if (mounted) setState(() => _loadingGallery = false);
    }
  }

  Future<void> _criarGaleria() async {
    HapticFeedback.mediumImpact();
    try {
      await GalleryService.instance.createGallery(_uid);
      if (mounted) {
        setState(() => _hasGallery = true);
        _snack('Galeria criada! ✨', success: true);
      }
    } catch (e) {
      debugPrint('_criarGaleria error: $e');
      if (mounted) _snack('Erro ao criar galeria. Tente novamente.');
    }
  }

  Future<void> _adicionarAGaleria() async {
    HapticFeedback.selectionClick();
    final ok = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => CreateGalleryItemScreen(userData: widget.userData),
      ),
    );
    if (ok == true) _carregarGaleria();
  }

  void _abrirGalleryItem(GalleryItem item) {
    HapticFeedback.selectionClick();
    if (item.type == 'video') {
      Navigator.push(
        context,
        FullscreenVideoScreen.route(
          postId: item.id,
          videoUrl: item.mediaUrl,
          thumbUrl: item.thumbUrl,
          userName: _localUserData['name'] ?? 'Você',
          titulo: 'Galeria',
          duration: item.videoDuration,
        ),
      );
    } else {
      Navigator.push(
        context,
        FullscreenImageScreen.route(
          imageUrl: item.mediaUrl,
          userName: _localUserData['name'] ?? 'Você',
          titulo: 'Galeria',
        ),
      );
    }
  }

  Future<void> _deletarGalleryItem(GalleryItem item) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: TabuColors.bgAlt,
        title: const Text(
          'EXCLUIR DA GALERIA?',
          style: TextStyle(
            fontFamily: TabuTypography.displayFont,
            fontSize: 14,
            letterSpacing: 4,
            color: TabuColors.branco,
          ),
        ),
        content: const Text(
          'Esta ação não pode ser desfeita.',
          style: TextStyle(
            fontFamily: TabuTypography.bodyFont,
            fontSize: 12,
            color: TabuColors.subtle,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('CANCELAR',
                style: TextStyle(color: TabuColors.dim)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('EXCLUIR',
                style: TextStyle(color: Color(0xFFE85D5D))),
          ),
        ],
      ),
    );

    if (confirm == true) {
      HapticFeedback.mediumImpact();
      try {
        if (item.type == 'video') {
          await VideoPreloadService.instance.evict(item.id);
        }
        await GalleryService.instance.deleteItem(_uid, item.id);
        _carregarGaleria();
        if (mounted) _snack('Item removido da galeria', success: true);
      } catch (e) {
        debugPrint('_deletarGalleryItem error: $e');
        if (mounted) _snack('Erro ao remover item.');
      }
    }
  }

  void _abrirPost(PostModel post) {
    HapticFeedback.selectionClick();
    if (post.tipo == 'video' && post.mediaUrl != null) {
      Navigator.push(
        context,
        FullscreenVideoScreen.route(
          postId: post.id,
          videoUrl: post.mediaUrl!,
          thumbUrl: post.thumbUrl,
          userName: _localUserData['name'] ?? 'Você',
          titulo: post.titulo,
          duration: post.videoDuration,
        ),
      );
    } else if (post.tipo == 'foto' && post.mediaUrl != null) {
      Navigator.push(
        context,
        FullscreenImageScreen.route(
          imageUrl: post.mediaUrl!,
          userName: _localUserData['name'] ?? 'Você',
          titulo: post.titulo,
        ),
      );
    } else {
      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        backgroundColor: Colors.transparent,
        barrierColor: Colors.black.withOpacity(0.75),
        builder: (_) => PostDetailSheet(post: post, myUid: _uid),
      );
    }
  }

  void _snack(String msg, {bool success = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor:
            success ? TabuColors.rosaDeep : const Color(0xFF3D0A0A),
        behavior: SnackBarBehavior.floating,
        shape: const RoundedRectangleBorder(),
        margin: const EdgeInsets.all(16),
        duration: const Duration(seconds: 3),
        content: Text(
          msg,
          style: const TextStyle(
            fontFamily: TabuTypography.bodyFont,
            fontSize: 12,
            fontWeight: FontWeight.w700,
            letterSpacing: 1.5,
            color: TabuColors.branco,
          ),
        ),
      ),
    );
  }

  void _showConfigMenu() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => ConfigMenu(
        isAdmin: _isAdmin,
        onSignOut: _signOut,
        onAbrirAdmin: _abrirAdmin,
      ),
    );
  }

  Future<void> _signOut() async {
    final confirm = await showModalBottomSheet<bool>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => const SignOutSheet(),
    );
    if (confirm == true && mounted) {
      AdminService.instance.clearCache();
      await AuthService().signOut();
      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
          PageRouteBuilder(
            pageBuilder: (_, animation, __) => const AccessCodeScreen(),
            transitionsBuilder: (_, animation, __, child) => FadeTransition(
              opacity:
                  CurvedAnimation(parent: animation, curve: Curves.easeOut),
              child: child,
            ),
            transitionDuration: const Duration(milliseconds: 400),
          ),
          (route) => false,
        );
      }
    }
  }

  void _abrirAdmin() {
    HapticFeedback.mediumImpact();
    Navigator.push(
      context,
      PageRouteBuilder(
        pageBuilder: (_, animation, __) => AdminPanelScreen(adminUid: _uid),
        transitionsBuilder: (_, animation, __, child) => SlideTransition(
          position: Tween<Offset>(begin: const Offset(1, 0), end: Offset.zero)
              .animate(CurvedAnimation(
                  parent: animation, curve: Curves.easeOutCubic)),
          child: child,
        ),
        transitionDuration: const Duration(milliseconds: 300),
      ),
    );
  }

  Future<void> _openEdit() async {
    final updated = await Navigator.push<Map<String, dynamic>>(
      context,
      MaterialPageRoute(
        builder: (_) => EditPerfilScreen(
          userData: _localUserData,
          onSaved: (data) =>
              setState(() => _localUserData = {..._localUserData, ...data}),
        ),
      ),
    );
    if (updated != null && mounted) {
      setState(() => _localUserData = {..._localUserData, ...updated});
    }
  }

  void _abrirStoryViewer() {
    if (_myStories.isEmpty) return;
    HapticFeedback.selectionClick();
    Navigator.push(
      context,
      PageRouteBuilder(
        pageBuilder: (_, animation, __) => StoryViewerScreen(
          storiesByUser: {_uid: _myStories},
          initialUserId: _uid,
          myUid: _uid,
          onStoriesChanged: _carregarStories,
        ),
        transitionsBuilder: (_, animation, __, child) => FadeTransition(
          opacity: CurvedAnimation(parent: animation, curve: Curves.easeOut),
          child: child,
        ),
        transitionDuration: const Duration(milliseconds: 200),
      ),
    );
  }

  void _abrirPerfil(String userId) {
    HapticFeedback.selectionClick();
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) =>
            PublicProfileScreen(userId: userId, userName: userId),
      ),
    );
  }

  void _openSheet({
    required String title,
    required IconData icon,
    required Color accentColor,
    required Widget content,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => MetricSheet(
        title: title,
        icon: icon,
        accentColor: accentColor,
        content: content,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final data = UserDataNotifier.instance.value.isNotEmpty
        ? UserDataNotifier.instance.value
        : _localUserData;
    final name = (data['name'] as String? ?? 'Usuário').toUpperCase();
    final email = data['email'] as String? ?? '';
    final bio =
        ((data['bio'] as String?) ?? (data['bio '] as String?) ?? '').trim();
    final avatarUrl = data['avatar'] as String? ?? '';
    final bairro = (data['bairro'] as String? ?? '').trim();
    final cidade = (data['city'] as String? ?? '').trim();
    final estado = (data['state'] as String? ?? '').trim();
    final localizacao =
        [bairro, cidade, estado].where((s) => s.isNotEmpty).join(', ');
    final temStory = _myStories.isNotEmpty;

    return Scaffold(
      backgroundColor: TabuColors.bg,
      body: Stack(
        children: [
          Positioned.fill(child: CustomPaint(painter: PerfilBg())),
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 3,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    TabuColors.rosaDeep,
                    TabuColors.rosaPrincipal,
                    TabuColors.rosaClaro,
                    TabuColors.rosaPrincipal,
                    TabuColors.rosaDeep,
                  ],
                ),
              ),
            ),
          ),
          SafeArea(
            child: RefreshIndicator(
              color: TabuColors.rosaPrincipal,
              backgroundColor: TabuColors.bgAlt,
              onRefresh: _carregarTudo,
              child: CustomScrollView(
                physics: const BouncingScrollPhysics(),
                slivers: [
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          const SizedBox(height: 12),

                          // ── Top bar ──────────────────────────────────────
                          Row(
                            children: [
                              if (_isAdmin && !_loadingAdmin)
                                GestureDetector(
                                  onTap: _abrirAdmin,
                                  child: Container(
                                    height: 38,
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 12),
                                    decoration: BoxDecoration(
                                      color: TabuColors.rosaDeep
                                          .withOpacity(0.2),
                                      border: Border.all(
                                        color: TabuColors.rosaPrincipal
                                            .withOpacity(0.5),
                                        width: 0.8,
                                      ),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: const [
                                        Icon(Icons.shield_rounded,
                                            color: TabuColors.rosaPrincipal,
                                            size: 13),
                                        SizedBox(width: 6),
                                        Text(
                                          'ADMIN',
                                          style: TextStyle(
                                            fontFamily:
                                                TabuTypography.bodyFont,
                                            fontSize: 9,
                                            fontWeight: FontWeight.w700,
                                            letterSpacing: 2,
                                            color: TabuColors.rosaPrincipal,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                )
                              else
                                const SizedBox(width: 38),
                              const Spacer(),
                              GestureDetector(
                                onTap: _showConfigMenu,
                                child: Container(
                                  width: 38,
                                  height: 38,
                                  decoration: BoxDecoration(
                                    color: TabuColors.bgCard,
                                    border: Border.all(
                                        color: TabuColors.border, width: 0.8),
                                  ),
                                  child: const Icon(
                                      Icons.settings_outlined,
                                      color: TabuColors.subtle,
                                      size: 18),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),

                          // Avatar
                          GestureDetector(
                            onTap:
                                temStory ? _abrirStoryViewer : _openEdit,
                            child: Stack(
                              alignment: Alignment.center,
                              children: [
                                AnimatedContainer(
                                  duration:
                                      const Duration(milliseconds: 300),
                                  width: 100,
                                  height: 100,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    gradient: temStory
                                        ? const LinearGradient(
                                            colors: [
                                              TabuColors.rosaDeep,
                                              TabuColors.rosaPrincipal,
                                              TabuColors.rosaClaro,
                                            ],
                                            begin: Alignment.topLeft,
                                            end: Alignment.bottomRight,
                                          )
                                        : null,
                                    color: temStory
                                        ? null
                                        : TabuColors.border,
                                    boxShadow: temStory
                                        ? [
                                            BoxShadow(
                                              color: TabuColors.glow,
                                              blurRadius: 20,
                                              spreadRadius: 2,
                                            )
                                          ]
                                        : null,
                                  ),
                                ),
                                Container(
                                  width: 93,
                                  height: 93,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                        color: TabuColors.bg, width: 2.5),
                                  ),
                                ),
                                Avatar(
                                    avatarUrl: avatarUrl,
                                    showCamera: !temStory),
                              ],
                            ),
                          ),

                          const SizedBox(height: 16),

                          // Nome
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                name,
                                style: Theme.of(context)
                                    .textTheme
                                    .displaySmall
                                    ?.copyWith(
                                  fontSize: 30,
                                  letterSpacing: 6,
                                  color: TabuColors.branco,
                                  fontWeight: FontWeight.w400,
                                  shadows: [
                                    Shadow(
                                        color: TabuColors.glow,
                                        blurRadius: 20)
                                  ],
                                ),
                              ),
                              if (_isAdmin && !_loadingAdmin) ...[
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 6, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: TabuColors.rosaDeep
                                        .withOpacity(0.25),
                                    border: Border.all(
                                      color: TabuColors.rosaPrincipal
                                          .withOpacity(0.5),
                                      width: 0.8,
                                    ),
                                  ),
                                  child: const Icon(Icons.shield_rounded,
                                      color: TabuColors.rosaPrincipal,
                                      size: 10),
                                ),
                              ],
                            ],
                          ),
                          const SizedBox(height: 6),

                          Text(
                            email,
                            style: const TextStyle(
                              fontFamily: TabuTypography.bodyFont,
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                              letterSpacing: 1.5,
                              color: TabuColors.dim,
                            ),
                          ),

                          if (localizacao.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 16),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.location_on_outlined,
                                      color: TabuColors.rosaPrincipal,
                                      size: 12),
                                  const SizedBox(width: 4),
                                  Flexible(
                                    child: Text(
                                      localizacao.toUpperCase(),
                                      textAlign: TextAlign.center,
                                      overflow: TextOverflow.ellipsis,
                                      maxLines: 2,
                                      style: const TextStyle(
                                        fontFamily: TabuTypography.bodyFont,
                                        fontSize: 10,
                                        fontWeight: FontWeight.w600,
                                        letterSpacing: 2,
                                        color: TabuColors.rosaPrincipal,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],

                          if (bio.isNotEmpty) ...[
                            const SizedBox(height: 10),
                            Text(
                              bio,
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                fontFamily: TabuTypography.bodyFont,
                                fontSize: 13,
                                letterSpacing: 0.5,
                                color: TabuColors.dim,
                                height: 1.5,
                              ),
                            ),
                          ],

                          const SizedBox(height: 24),
                          Container(
                              height: 0.5, color: TabuColors.border),
                          const SizedBox(height: 16),

                          // Editar perfil
                          GestureDetector(
                            onTap: _openEdit,
                            child: Container(
                              width: double.infinity,
                              height: 46,
                              decoration: BoxDecoration(
                                color: TabuColors.bgCard,
                                border: Border.all(
                                    color: TabuColors.borderMid, width: 0.8),
                              ),
                              child: const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.edit_outlined,
                                      color: TabuColors.rosaPrincipal,
                                      size: 15),
                                  SizedBox(width: 10),
                                  Text(
                                    'EDITAR PERFIL',
                                    style: TextStyle(
                                      fontFamily: TabuTypography.bodyFont,
                                      fontSize: 11,
                                      fontWeight: FontWeight.w700,
                                      letterSpacing: 3,
                                      color: TabuColors.rosaPrincipal,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                          if (_isAdmin && !_loadingAdmin) ...[
                            const SizedBox(height: 10),
                            GestureDetector(
                              onTap: _abrirAdmin,
                              child: Container(
                                width: double.infinity,
                                height: 46,
                                decoration: BoxDecoration(
                                  color: TabuColors.rosaDeep
                                      .withOpacity(0.15),
                                  border: Border.all(
                                    color: TabuColors.rosaPrincipal
                                        .withOpacity(0.5),
                                    width: 0.8,
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: TabuColors.glow
                                          .withOpacity(0.15),
                                      blurRadius: 12,
                                    ),
                                  ],
                                ),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: const [
                                    Icon(Icons.shield_rounded,
                                        color: TabuColors.rosaPrincipal,
                                        size: 15),
                                    SizedBox(width: 10),
                                    Text(
                                      'PAINEL PROFISSIONAL',
                                      style: TextStyle(
                                        fontFamily: TabuTypography.bodyFont,
                                        fontSize: 11,
                                        fontWeight: FontWeight.w700,
                                        letterSpacing: 3,
                                        color: TabuColors.rosaPrincipal,
                                      ),
                                    ),
                                    SizedBox(width: 10),
                                    Icon(Icons.arrow_forward_ios_rounded,
                                        color: TabuColors.rosaPrincipal,
                                        size: 10),
                                  ],
                                ),
                              ),
                            ),
                          ],

                          const SizedBox(height: 20),

                          // Stats
                          Row(
                            children: [
                              StatCard(
                                value: _loadingPosts
                                    ? '—'
                                    : '${_posts.length}',
                                label: 'POSTS',
                                icon: Icons.grid_view_rounded,
                                onTap: () {},
                              ),
                              const SizedBox(width: 10),
                              StatCard(
                                value: _loadingFollowers
                                    ? '—'
                                    : '${_followers.length}',
                                label: 'SEGUIDORES',
                                icon: Icons.people_outline_rounded,
                                onTap: () => _openSheet(
                                  title: 'SEGUIDORES',
                                  icon: Icons.people_outline_rounded,
                                  accentColor: TabuColors.rosaClaro,
                                  content: UserList(
                                    uids: _followers,
                                    emptyLabel: 'Nenhum seguidor ainda',
                                    onTap: _abrirPerfil,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 10),
                              StatCard(
                                value: _loadingVip
                                    ? '—'
                                    : '${_vipFriends.length}',
                                label: 'AMIGOS VIP',
                                icon: Icons.star_border_rounded,
                                highlight: true,
                                onTap: () => _openSheet(
                                  title: 'AMIGOS VIP',
                                  icon: Icons.star_rounded,
                                  accentColor: const Color(0xFFD4AF37),
                                  content: UserList(
                                    uids: _vipFriends,
                                    emptyLabel: 'Nenhum amigo VIP ainda',
                                    onTap: _abrirPerfil,
                                    isVip: true,
                                  ),
                                ),
                              ),
                            ],
                          ),

                          const SizedBox(height: 16),
                          VipFriendsBadge(
                              count:
                                  _loadingVip ? 0 : _vipFriends.length),

                          // Tabs
                          const SizedBox(height: 24),
                          Container(
                            decoration: BoxDecoration(
                              color: TabuColors.bgCard,
                              border: Border.all(
                                  color: TabuColors.border, width: 0.8),
                            ),
                            child: TabBar(
                              controller: _tabController,
                              indicatorColor: TabuColors.rosaPrincipal,
                              indicatorWeight: 2,
                              labelColor: TabuColors.rosaPrincipal,
                              unselectedLabelColor: TabuColors.subtle,
                              dividerColor: Colors.transparent,
                              labelStyle: const TextStyle(
                                fontFamily: TabuTypography.bodyFont,
                                fontSize: 10,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 2.5,
                              ),
                              unselectedLabelStyle: const TextStyle(
                                fontFamily: TabuTypography.bodyFont,
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 2.5,
                              ),
                              tabs: [
                                Tab(
                                  icon: const Icon(
                                      Icons.grid_view_rounded,
                                      size: 14),
                                  text:
                                      'PUBLICAÇÕES${_loadingPosts ? '' : ' · ${_posts.length}'}',
                                ),
                                Tab(
                                  icon: const Icon(
                                      Icons.photo_library_outlined,
                                      size: 14),
                                  text:
                                      'GALERIA${_loadingGallery ? '' : _hasGallery ? ' · ${_galleryItems.length}' : ''}',
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 4),
                        ],
                      ),
                    ),
                  ),

                  // ── CONTEÚDO DAS TABS ──────────────────────────────────
                  if (_tabController.index == 0) ...[
                    if (_loadingPosts)
                      const GaleriaSkeleton()
                    else if (_posts.isEmpty)
                      SliverFillRemaining(
                          hasScrollBody: false, child: _buildVazio())
                    else
                      // ✅ FIX: EdgeInsets.zero evita overflow lateral
                      SliverPadding(
                        padding: const EdgeInsets.symmetric(horizontal: 24),
                        sliver: SliverGrid(
                          delegate: SliverChildBuilderDelegate(
                            (_, i) => _PostGridTile(
                              post: _posts[i],
                              myUid: _uid,
                              onTap: () => _abrirPost(_posts[i]),
                            ),
                            childCount: _posts.length,
                          ),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 3,
                            crossAxisSpacing: 1.5,
                            mainAxisSpacing: 1.5,
                            childAspectRatio: 1,
                          ),
                        ),
                      ),
                  ] else ...[
                    if (_loadingGallery)
                      const GaleriaSkeleton()
                    else if (!_hasGallery)
                      SliverFillRemaining(
                        hasScrollBody: false,
                        child: _buildGaleriaNaoCriada(),
                      )
                    else if (_galleryItems.isEmpty)
                      SliverFillRemaining(
                        hasScrollBody: false,
                        child: _buildGaleriaVazia(),
                      )
                    else
                      // ✅ FIX: EdgeInsets.zero evita overflow lateral
                      SliverPadding(
                        padding: const EdgeInsets.symmetric(horizontal: 24),
                        sliver: SliverGrid(
                          delegate: SliverChildBuilderDelegate(
                            (_, i) => _GalleryGridTile(
                              item: _galleryItems[i],
                              isPreloaded: VideoPreloadService.instance
                                  .isReady(_galleryItems[i].id),
                              onTap: () =>
                                  _abrirGalleryItem(_galleryItems[i]),
                              onDelete: () =>
                                  _deletarGalleryItem(_galleryItems[i]),
                            ),
                            childCount: _galleryItems.length,
                          ),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 3,
                            crossAxisSpacing: 1.5,
                            mainAxisSpacing: 1.5,
                            childAspectRatio: 1,
                          ),
                        ),
                      ),
                  ],

                  const SliverToBoxAdapter(child: SizedBox(height: 100)),
                ],
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: _tabController.index == 1 && !_loadingGallery
          ? FloatingActionButton(
              onPressed: _adicionarAGaleria,
              backgroundColor: TabuColors.rosaPrincipal,
              elevation: 8,
              heroTag: 'gallery_fab',
              child: const Icon(Icons.add, color: Colors.white, size: 28),
            )
          : null,
    );
  }

  Widget _buildVazio() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: BoxDecoration(
              border: Border.all(color: TabuColors.border, width: 0.8),
              color: TabuColors.bgCard,
            ),
            child: const Icon(Icons.photo_library_outlined,
                color: TabuColors.border, size: 20),
          ),
          const SizedBox(height: 16),
          const Text(
            'SEM PUBLICAÇÕES',
            style: TextStyle(
              fontFamily: TabuTypography.bodyFont,
              fontSize: 9,
              fontWeight: FontWeight.w700,
              letterSpacing: 4,
              color: TabuColors.subtle,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGaleriaNaoCriada() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                border: Border.all(color: TabuColors.border, width: 0.8),
                color: TabuColors.bgCard,
              ),
              child: const Icon(Icons.photo_library_outlined,
                  color: TabuColors.border, size: 28),
            ),
            const SizedBox(height: 20),
            const Text(
              'SUA GALERIA PESSOAL',
              style: TextStyle(
                fontFamily: TabuTypography.displayFont,
                fontSize: 16,
                letterSpacing: 5,
                color: TabuColors.branco,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Crie sua galeria para guardar fotos e vídeos que aparecem apenas no seu perfil.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: TabuTypography.bodyFont,
                fontSize: 12,
                letterSpacing: 0.3,
                color: TabuColors.subtle,
                height: 1.6,
              ),
            ),
            const SizedBox(height: 28),
            GestureDetector(
              onTap: _criarGaleria,
              child: Container(
                width: double.infinity,
                height: 50,
                decoration: BoxDecoration(
                  color: TabuColors.rosaPrincipal,
                  boxShadow: [
                    BoxShadow(
                      color: TabuColors.glow.withOpacity(0.35),
                      blurRadius: 16,
                      spreadRadius: 1,
                    )
                  ],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Icon(Icons.add_photo_alternate_rounded,
                        color: Colors.white, size: 18),
                    SizedBox(width: 10),
                    Text(
                      'CRIAR GALERIA',
                      style: TextStyle(
                        fontFamily: TabuTypography.bodyFont,
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 3,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGaleriaVazia() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            GestureDetector(
              onTap: _adicionarAGaleria,
              child: Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  border: Border.all(color: TabuColors.border, width: 0.8),
                  color: TabuColors.bgCard,
                ),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    const Icon(Icons.add_photo_alternate_outlined,
                        color: TabuColors.border, size: 28),
                    Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: TabuColors.rosaPrincipal,
                        boxShadow: [
                          BoxShadow(
                            color: TabuColors.glow.withOpacity(0.4),
                            blurRadius: 12,
                            spreadRadius: 1,
                          )
                        ],
                      ),
                      child: const Icon(Icons.add,
                          color: Colors.white, size: 20),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'GALERIA VAZIA',
              style: TextStyle(
                fontFamily: TabuTypography.bodyFont,
                fontSize: 10,
                fontWeight: FontWeight.w700,
                letterSpacing: 4,
                color: TabuColors.subtle,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Toque no + para adicionar fotos e vídeos',
              style: TextStyle(
                fontFamily: TabuTypography.bodyFont,
                fontSize: 12,
                color: TabuColors.subtle,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
//  GALLERY GRID TILE
// ══════════════════════════════════════════════════════════════════════════════
class _GalleryGridTile extends StatelessWidget {
  final GalleryItem item;
  final VoidCallback onTap;
  final VoidCallback onDelete;
  final bool isPreloaded;

  const _GalleryGridTile({
    required this.item,
    required this.onTap,
    required this.onDelete,
    this.isPreloaded = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      onLongPress: () {
        HapticFeedback.heavyImpact();
        showModalBottomSheet(
          context: context,
          backgroundColor: TabuColors.bgAlt,
          shape: const RoundedRectangleBorder(),
          builder: (_) => SafeArea(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 36,
                  height: 3,
                  margin: const EdgeInsets.only(top: 12, bottom: 20),
                  decoration: BoxDecoration(
                    color: TabuColors.border,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                PDSMenuTile(
                  icon: Icons.delete_outline_rounded,
                  label: 'REMOVER DA GALERIA',
                  sublabel: 'Excluir permanentemente',
                  danger: true,
                  onTap: () {
                    Navigator.pop(context);
                    onDelete();
                  },
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        );
      },
      child: Container(
        color: TabuColors.bgCard,
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (item.type == 'video' && item.thumbUrl != null)
              Image.network(item.thumbUrl!,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _fundo())
            else if (item.type == 'foto')
              Image.network(item.mediaUrl,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _fundo())
            else
              _fundo(),
            if (item.type == 'video') ...[
              Positioned.fill(
                child: Container(
                  decoration: BoxDecoration(
                    gradient: RadialGradient(
                      center: Alignment.center,
                      radius: 0.88,
                      colors: [
                        Colors.transparent,
                        Colors.black.withOpacity(0.25),
                      ],
                    ),
                  ),
                ),
              ),
              Center(
                child: Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.black.withOpacity(0.6),
                    border: Border.all(
                      color: isPreloaded
                          ? const Color(0xFF22C55E)
                          : TabuColors.rosaPrincipal,
                      width: 1.2,
                    ),
                  ),
                  child: const Icon(Icons.play_arrow_rounded,
                      color: Colors.white, size: 20),
                ),
              ),
              if (item.videoDuration != null)
                Positioned(
                  bottom: 6,
                  right: 6,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 5, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.7),
                      borderRadius: BorderRadius.circular(2),
                    ),
                    child: Text(
                      _formatDuration(item.videoDuration!),
                      style: const TextStyle(
                        fontFamily: TabuTypography.bodyFont,
                        fontSize: 9,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              if (isPreloaded)
                Positioned(
                  top: 5,
                  left: 5,
                  child: Container(
                    width: 18,
                    height: 18,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: const Color(0xFF22C55E).withOpacity(0.85),
                    ),
                    child: const Icon(Icons.bolt_rounded,
                        color: Colors.white, size: 11),
                  ),
                ),
            ] else
              Positioned(
                top: 6,
                right: 6,
                child: Container(
                  width: 22,
                  height: 22,
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.5),
                    borderRadius: BorderRadius.circular(2),
                  ),
                  child: const Icon(Icons.photo_outlined,
                      color: Colors.white, size: 12),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _fundo() => Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF2D0010), Color(0xFF7A0028)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
      );

  String _formatDuration(int seconds) {
    final m = (seconds ~/ 60).toString().padLeft(2, '0');
    final s = (seconds % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }
}

// ══════════════════════════════════════════════════════════════════════════════
//  POST GRID TILE
// ══════════════════════════════════════════════════════════════════════════════
class _PostGridTile extends StatelessWidget {
  final PostModel post;
  final String myUid;
  final VoidCallback onTap;

  const _PostGridTile({
    required this.post,
    required this.myUid,
    required this.onTap,
  });

  List<Color> _gradient() {
    final p = [
      [const Color(0xFF3D0018), const Color(0xFF6B0030)],
      [const Color(0xFF1A0030), const Color(0xFF4B005A)],
      [const Color(0xFF2D0010), const Color(0xFF7A0028)],
      [const Color(0xFF0D0020), const Color(0xFF3B0050)],
      [const Color(0xFF2A0012), const Color(0xFFCC0044)],
    ];
    return p[post.userId.codeUnits.fold(0, (a, b) => a + b) % p.length];
  }

  String _formatDuration(int seconds) {
    final m = (seconds ~/ 60).toString().padLeft(2, '0');
    final s = (seconds % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        color: TabuColors.bgCard,
        child: Stack(fit: StackFit.expand, children: [
          if (post.tipo == 'foto' && post.mediaUrl != null)
            Image.network(post.mediaUrl!,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => _fundo())
          else if (post.tipo == 'video' && post.thumbUrl != null)
            Image.network(post.thumbUrl!,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => _fundo())
          else
            _fundo(),
          if (post.tipo == 'video') ...[
            Positioned.fill(
              child: Container(
                decoration: BoxDecoration(
                  gradient: RadialGradient(
                    center: Alignment.center,
                    radius: 0.88,
                    colors: [
                      Colors.transparent,
                      Colors.black.withOpacity(0.3),
                    ],
                  ),
                ),
              ),
            ),
            Center(
              child: Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.black.withOpacity(0.6),
                  border: Border.all(
                      color: TabuColors.rosaPrincipal, width: 1.2),
                ),
                child: const Icon(Icons.play_arrow_rounded,
                    color: Colors.white, size: 20),
              ),
            ),
            if (post.videoDuration != null)
              Positioned(
                bottom: 6,
                right: 6,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 5, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.7),
                    borderRadius: BorderRadius.circular(2),
                  ),
                  child: Text(
                    _formatDuration(post.videoDuration!),
                    style: const TextStyle(
                      fontFamily: TabuTypography.bodyFont,
                      fontSize: 9,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
          ],
          if (post.tipo == 'emoji' && post.emoji != null)
            Center(
                child: Text(post.emoji!,
                    style: const TextStyle(fontSize: 30))),
          if (post.tipo == 'texto')
            Center(
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Text(
                  post.titulo,
                  maxLines: 4,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontFamily: TabuTypography.bodyFont,
                    fontSize: 8,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                    letterSpacing: 0.5,
                    height: 1.4,
                  ),
                ),
              ),
            ),
          if (post.tipo == 'foto')
            Positioned(
              top: 6,
              right: 6,
              child: Container(
                width: 22,
                height: 22,
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(2),
                ),
                child: const Icon(Icons.photo_outlined,
                    color: Colors.white, size: 12),
              ),
            ),
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: Alignment.center,
                  radius: 0.88,
                  colors: [
                    Colors.transparent,
                    Colors.black.withOpacity(0.18),
                  ],
                ),
              ),
            ),
          ),
        ]),
      ),
    );
  }

  Widget _fundo() {
    final g = _gradient();
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: g,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
    );
  }
}
