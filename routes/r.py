
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from db import getDB
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# 作者投稿清單
@router.get("/author")
async def author_list(request: Request, db=Depends(getDB)):
    cur = await db.execute(
        """
        SELECT *
        FROM articles
        WHERE author_id = 1
        ORDER BY id;
        """
    )
    data = await cur.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="author.html",
        context={"articles": data}
    )

# 新增投稿頁面
@router.get("/author/new")
async def author_new(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="author_new.html",
        context={}
    )
# 儲存新增投稿
@router.post("/author/create")
async def author_create(
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db=Depends(getDB)
):
    await db.execute(
        """
        INSERT INTO articles (author_id, category, title, content, status)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (1, category, title, content, "編輯中")
    )

    return RedirectResponse(
        url="/author",
        status_code=303
    )
# 編輯投稿頁面
@router.get("/author/edit/{article_id}")
async def author_edit(
    article_id: int,
    request: Request,
    db=Depends(getDB)
):
    cur = await db.execute(
        """
        SELECT *
        FROM articles
        WHERE id = %s
        AND author_id = 1
        AND status = '編輯中';
        """,
        (article_id,)
    )

    article = await cur.fetchone()

    if article is None:
        return HTMLResponse("找不到文章，或文章目前無法編輯", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="author_edit.html",
        context={"article": article}
    )
# 儲存修改投稿
@router.post("/author/update")
async def author_update(
    id: int = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db=Depends(getDB)
):
    await db.execute(
        """
        UPDATE articles
        SET category = %s,
            title = %s,
            content = %s
        WHERE id = %s
        AND author_id = 1
        AND status = '編輯中';
        """,
        (category, title, content, id)
    )

    return RedirectResponse(
        url="/author",
        status_code=303
    )
# 刪除投稿
@router.post("/author/delete/{article_id}")
async def author_delete(
    article_id: int,
    db=Depends(getDB)
):
    await db.execute(
        """
        DELETE FROM articles
        WHERE id = %s
        AND author_id = 1
        AND status = '編輯中';
        """,
        (article_id,)
    )

    return RedirectResponse(
        url="/author",
        status_code=303
    )
# 送出投稿審查
@router.post("/author/submit/{article_id}")
async def author_submit(
    article_id: int,
    db=Depends(getDB)
):
    await db.execute(
        """
        UPDATE articles
        SET status = '審查中'
        WHERE id = %s
        AND author_id = 1
        AND status = '編輯中';
        """,
        (article_id,)
    )

    return RedirectResponse(
        url="/author",
        status_code=303
    )
# 編輯待審查清單
@router.get("/editor")
async def editor_list(request: Request, db=Depends(getDB)):
    cur = await db.execute(
        """
        SELECT
            articles.id,
            authors.display_name AS author_name,
            articles.category,
            articles.title
        FROM articles
        JOIN authors ON articles.author_id = authors.id
        WHERE articles.status = '審查中'
        ORDER BY articles.id;
        """
    )

    data = await cur.fetchall()

    return templates.TemplateResponse(
        request=request,
        name="editor.html",
        context={"articles": data}
    )
# 查看待審查稿件內容
@router.get("/editor/article/{article_id}")
async def editor_article(
    article_id: int,
    request: Request,
    db=Depends(getDB)
):
    cur = await db.execute(
        """
        SELECT
            articles.*,
            authors.display_name AS author_name
        FROM articles
        JOIN authors ON articles.author_id = authors.id
        WHERE articles.id = %s
        AND articles.status = '審查中';
        """,
        (article_id,)
    )

    article = await cur.fetchone()

    if article is None:
        return HTMLResponse("找不到稿件，或稿件目前不在審查中", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="editor_article.html",
        context={"article": article}
    )
# 通過稿件
@router.post("/editor/approve/{article_id}")
async def editor_approve(
    article_id: int,
    db=Depends(getDB)
):
    await db.execute(
        """
        UPDATE articles
        SET status = '已通過'
        WHERE id = %s
        AND status = '審查中';
        """,
        (article_id,)
    )

    return RedirectResponse(
        url="/editor",
        status_code=303
    )
# 退回稿件
@router.post("/editor/reject/{article_id}")
async def editor_reject(
    article_id: int,
    db=Depends(getDB)
):
    await db.execute(
        """
        UPDATE articles
        SET status = '編輯中'
        WHERE id = %s
        AND status = '審查中';
        """,
        (article_id,)
    )

    return RedirectResponse(
        url="/editor",
        status_code=303
    )